import os, re, datetime, logging, csv, pytz
from urllib import parse
from django.utils import timezone
from datetime import timedelta
from rest_framework_csv.renderers import CSVRenderer
from breathecode.renderers import PlainTextRenderer
from rest_framework.decorators import renderer_classes
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseNotFound, HttpResponse, HttpResponseRedirect
from django.contrib.auth.models import AnonymousUser
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q
from rest_framework.permissions import AllowAny
from rest_framework.decorators import api_view, permission_classes
from django.db.models import Count, F, Func, Value, CharField
from breathecode.utils import (APIException, localize_query, capable_of, ValidationException,
                               GenerateLookupsMixin, HeaderLimitOffsetPagination)
from .serializers import (
    PostFormEntrySerializer,
    FormEntrySerializer,
    FormEntrySmallSerializer,
    TagSmallSerializer,
    AutomationSmallSerializer,
    DownloadableSerializer,
    ShortLinkSerializer,
)
from breathecode.services.activecampaign import ActiveCampaign
from .actions import register_new_lead, sync_tags, sync_automations, get_facebook_lead_info
from .tasks import persist_single_lead, update_link_viewcount, async_activecampaign_webhook
from .models import ShortLink, ActiveCampaignAcademy, FormEntry, Tag, Automation, Downloadable
from breathecode.admissions.models import Academy
from breathecode.utils.find_by_full_name import query_like_by_full_name
from rest_framework.views import APIView

logger = logging.getLogger(__name__)

# Create your views here.


@api_view(['GET'])
@permission_classes([AllowAny])
def get_downloadable(request, slug=None):

    if slug is not None:
        download = Downloadable.objects.filter(slug=slug).first()
        if download is None:
            raise APIException(f'Document not found', 404)

        if request.GET.get('raw', None) == 'true':
            return HttpResponseRedirect(redirect_to=download.destination_url)

        seri = DownloadableSerializer(download, many=False)
        return Response(seri.data)

    items = Downloadable.objects.all()
    academy = request.GET.get('academy', None)
    if academy is not None:
        items = items.filter(academy__slug__in=academy.split(','))

    active = request.GET.get('active', None)
    if active is not None:
        if active == 'true':
            active = True
        else:
            active = False
        items = items.filter(active=active)

    items = items.order_by('created_at')
    serializer = DownloadableSerializer(items, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([AllowAny])
def create_lead(request):
    serializer = PostFormEntrySerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()

        persist_single_lead.delay(serializer.data)

        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
@renderer_classes([PlainTextRenderer])
def activecampaign_webhook(request, ac_academy_id=None, academy_slug=None):

    if ac_academy_id is not None:
        a = Academy.objects.filter(slug=ac_academy_id).first()
        if a is None:
            raise APIException(f'Academy not found (id:{ac_academy_id}) ')
        webhook = ActiveCampaign.add_webhook_to_log(request.data, a.slug)
    elif academy_slug is not None:
        webhook = ActiveCampaign.add_webhook_to_log(request.data, academy_slug)
    else:
        raise APIException('Please specify a valid academy slug or id')

    if webhook:
        async_activecampaign_webhook.delay(webhook.id)
    else:
        logger.debug('One request cannot be parsed, maybe you should update `ActiveCampaign'
                     '.add_webhook_to_log`')
        #logger.debug(request.data)

    # async_eventbrite_webhook(request.data)
    return Response('ok', content_type='text/plain')


@api_view(['GET'])
@permission_classes([AllowAny])
@renderer_classes([CSVRenderer])
def googleads_enrollments(request, academy_slugs):

    slugs = academy_slugs.split(',')
    academies = FormEntry.objects.filter(Q(academy__slug__in=slugs)
                                         | Q(ac_academy__academy__slug__in=slugs)).exclude(gclid__isnull=True)

    serializer = FormEntrySerializer(academies, many=True)
    return Response(serializer.data)


# Create your views here.


@api_view(['POST', 'GET'])
@permission_classes([AllowAny])
def receive_facebook_lead(request):
    if request.method == 'GET':

        challenge = 'no challenge'
        if 'hub.challenge' in request.GET:
            challenge = request.GET['hub.challenge']

        verify_token = ''
        if 'hub.verify_token' in request.GET:
            verify_token = request.GET['hub.verify_token']

        mode = ''
        if 'hub.mode' in request.GET:
            mode = request.GET['hub.mode']

        if verify_token == os.getenv('FACEBOOK_VERIFY_TOKEN', ''):
            return Response(int(challenge), status=status.HTTP_200_OK)
        else:
            return Response(int(challenge), status=status.HTTP_400_BAD_REQUEST)
    else:
        if 'object' in request.data:
            if request.data['object'] == 'page':
                for entry in request.data['entry']:
                    for changes in entry['changes']:
                        if changes['field'] == 'leadgen':
                            serializer = PostFormEntrySerializer(
                                data={
                                    'fb_leadgen_id': changes['value']['leadgen_id'],
                                    'fb_page_id': changes['value']['page_id'],
                                    'fb_form_id': changes['value']['form_id'],
                                    'fb_adgroup_id': changes['value']['adgroup_id'],
                                    'fb_ad_id': changes['value']['ad_id']
                                })
                            if serializer.is_valid():
                                serializer.save()
                                # persist_single_lead.delay(request.data)
                                return Response(serializer.data, status=status.HTTP_201_CREATED)
                            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    return Response({'details': 'No leads found'}, status=status.HTTP_400_BAD_REQUEST)


# Create your views here.
@api_view(['GET'])
def sync_tags_with_active_campaign(request, academy_id):

    academy = ActiveCampaignAcademy.objects.filter(academy__id=academy_id).first()
    if academy is None:
        raise APIException('Academy not found')

    tags = sync_tags(academy)
    return Response(tags, status=status.HTTP_200_OK)


# Create your views here.


@api_view(['GET'])
def sync_automations_with_active_campaign(request, academy_id):

    academy = ActiveCampaignAcademy.objects.filter(academy__id=academy_id).first()
    if academy is None:
        raise APIException('Academy not found')

    tags = sync_automations(academy)
    return Response(tags, status=status.HTTP_200_OK)


def redirect_link(request, link_slug):
    short_link = ShortLink.objects.filter(slug=link_slug, active=True).first()
    if short_link is None:
        return HttpResponseNotFound('URL not found')

    update_link_viewcount.delay(short_link.slug)

    params = {}
    if short_link.utm_source is not None:
        params['utm_source'] = short_link.utm_source
    if short_link.utm_content is not None:
        params['utm_content'] = short_link.utm_content
    if short_link.utm_medium is not None:
        params['utm_medium'] = short_link.utm_medium
    if short_link.utm_campaign is not None:
        params['utm_campaign'] = short_link.utm_campaign

    destination_params = {}
    url_parts = short_link.destination.split('?')
    if len(url_parts) > 1:
        destination_params = dict(parse.parse_qsl(url_parts[1]))

    params = {**destination_params, **params}
    return HttpResponseRedirect(redirect_to=url_parts[0] + '?' + parse.urlencode(params))


@api_view(['GET'])
def get_leads(request, id=None):

    items = FormEntry.objects.all()
    if isinstance(request.user, AnonymousUser) == False:
        items = localize_query(items, request)

    academy = request.GET.get('academy', None)
    if academy is not None:
        items = items.filter(academy__slug__in=academy.split(','))

    start = request.GET.get('start', None)
    if start is not None:
        start_date = datetime.datetime.strptime(start, '%Y-%m-%d').date()
        items = items.filter(created_at__gte=start_date)

    end = request.GET.get('end', None)
    if end is not None:
        end_date = datetime.datetime.strptime(end, '%Y-%m-%d').date()
        items = items.filter(created_at__lte=end_date)

    items = items.order_by('created_at')
    serializer = FormEntrySerializer(items, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def get_leads_report(request, id=None):

    items = FormEntry.objects.all()

    if isinstance(request.user, AnonymousUser) == False:
        # filter only to the local academy
        items = localize_query(items, request)

    group_by = request.GET.get('by', 'location,created_at__date,course')
    if group_by != '':
        group_by = group_by.split(',')
    else:
        group_by = ['location', 'created_at__date', 'course']

    academy = request.GET.get('academy', None)
    if academy is not None:
        items = items.filter(location__in=academy.split(','))

    start = request.GET.get('start', None)
    if start is not None:
        start_date = datetime.datetime.strptime(start, '%Y-%m-%d').date()
        items = items.filter(created_at__gte=start_date)

    end = request.GET.get('end', None)
    if end is not None:
        end_date = datetime.datetime.strptime(end, '%Y-%m-%d').date()
        items = items.filter(created_at__lte=end_date)

    items = items.values(*group_by).annotate(total_leads=Count('location'))

    if 'created_at__date' in group_by:
        items = items.annotate(created_date=Func(
            F('created_at'), Value('YYYYMMDD'), function='to_char', output_field=CharField()))
    # items = items.order_by('created_at')
    return Response(items)


class AcademyTagView(APIView, GenerateLookupsMixin):
    """
    List all snippets, or create a new snippet.
    """
    @capable_of('crud_lead')
    def get(self, request, format=None, academy_id=None):

        print('academy_id', academy_id)
        tags = Tag.objects.filter(ac_academy__academy__id=academy_id)

        serializer = TagSmallSerializer(tags, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class AcademyAutomationView(APIView, GenerateLookupsMixin):
    """
    List all snippets, or create a new snippet.
    """
    @capable_of('read_lead')
    def get(self, request, format=None, academy_id=None):

        tags = Automation.objects.filter(ac_academy__academy__id=academy_id)

        serializer = AutomationSmallSerializer(tags, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class AcademyWonLeadView(APIView, HeaderLimitOffsetPagination, GenerateLookupsMixin):
    """
    List all snippets, or create a new snippet.
    """
    @capable_of('read_won_lead')
    def get(self, request, format=None, academy_id=None):

        academy = Academy.objects.get(id=academy_id)
        items = FormEntry.objects.filter(academy__id=academy.id, deal_status='WON')
        lookup = {}

        start = request.GET.get('start', None)
        if start is not None:
            start_date = datetime.datetime.strptime(start, '%Y-%m-%d').date()
            lookup['created_at__gte'] = start_date

        end = request.GET.get('end', None)
        if end is not None:
            end_date = datetime.datetime.strptime(end, '%Y-%m-%d').date()
            lookup['created_at__lte'] = end_date

        if 'storage_status' in self.request.GET:
            param = self.request.GET.get('storage_status')
            lookup['storage_status'] = param

        if 'course' in self.request.GET:
            param = self.request.GET.get('course')
            lookup['course'] = param

        if 'location' in self.request.GET:
            param = self.request.GET.get('location')
            lookup['location'] = param

        sort_by = '-created_at'
        if 'sort' in self.request.GET and self.request.GET['sort'] != '':
            sort_by = self.request.GET.get('sort')

        items = items.filter(**lookup).order_by(sort_by)

        like = request.GET.get('like', None)
        if like is not None:
            items = query_like_by_full_name(like=like, items=items)

        page = self.paginate_queryset(items, request)
        serializer = FormEntrySmallSerializer(page, many=True)

        if self.is_paginate(request):
            return self.get_paginated_response(serializer.data)
        else:
            return Response(serializer.data, status=200)


class AcademyLeadView(APIView, HeaderLimitOffsetPagination, GenerateLookupsMixin):
    """
    List all snippets, or create a new snippet.
    """
    @capable_of('read_lead')
    def get(self, request, format=None, academy_id=None):

        academy = Academy.objects.get(id=academy_id)
        items = FormEntry.objects.filter(academy__id=academy.id)
        lookup = {}

        start = request.GET.get('start', None)
        if start is not None:
            start_date = datetime.datetime.strptime(start, '%Y-%m-%d').date()
            lookup['created_at__gte'] = start_date

        end = request.GET.get('end', None)
        if end is not None:
            end_date = datetime.datetime.strptime(end, '%Y-%m-%d').date()
            lookup['created_at__lte'] = end_date

        if 'storage_status' in self.request.GET:
            param = self.request.GET.get('storage_status')
            lookup['storage_status'] = param

        if 'deal_status' in self.request.GET:
            param = self.request.GET.get('deal_status')
            lookup['deal_status'] = param.upper()

        if 'course' in self.request.GET:
            param = self.request.GET.get('course')
            lookup['course'] = param

        if 'location' in self.request.GET:
            param = self.request.GET.get('location')
            lookup['location'] = param

        sort_by = '-created_at'
        if 'sort' in self.request.GET and self.request.GET['sort'] != '':
            sort_by = self.request.GET.get('sort')

        items = items.filter(**lookup).order_by(sort_by)

        like = request.GET.get('like', None)
        if like is not None:
            items = query_like_by_full_name(like=like, items=items)

        page = self.paginate_queryset(items, request)
        serializer = FormEntrySmallSerializer(page, many=True)

        if self.is_paginate(request):
            return self.get_paginated_response(serializer.data)
        else:
            return Response(serializer.data, status=200)

    @capable_of('crud_lead')
    def delete(self, request, academy_id=None):
        # TODO: here i don't add one single delete, because i don't know if it is required
        lookups = self.generate_lookups(request, many_fields=['id'])
        # automation_objects

        if not lookups:
            raise ValidationException('Missing parameters in the querystring', code=400)

        items = FormEntry.objects.filter(**lookups, academy__id=academy_id)

        for item in items:
            item.delete()

        return Response(None, status=status.HTTP_204_NO_CONTENT)


class ShortLinkView(APIView, HeaderLimitOffsetPagination, GenerateLookupsMixin):
    """
    List all snippets, or create a new snippet.
    """
    @capable_of('read_shortlink')
    def get(self, request, slug=None, academy_id=None):

        if slug is not None:
            link = ShortLink.objects.filter(slug=slug).first()
            if link is None or (link.private and link.academy.id != academy_id):
                raise ValidationError(
                    f'Shortlink with slug {slug} not found or its private and it belongs to another academy',
                    slug='shortlink-not-found')

        academy = Academy.objects.get(id=academy_id)
        items = ShortLink.objects.filter(Q(academy__id=academy.id) | Q(private=False))
        lookup = {}

        private = request.GET.get('private', None)
        if private == 'true':
            lookup['private'] = True

        sort_by = '-created_at'
        if 'sort' in self.request.GET and self.request.GET['sort'] != '':
            sort_by = self.request.GET.get('sort')

        items = items.filter(**lookup).order_by(sort_by)

        like = request.GET.get('like', None)
        if like is not None:
            items = items.filter(slug__icontains=like)

        page = self.paginate_queryset(items, request)
        serializer = ShortlinkSmallSerializer(page, many=True)

        if self.is_paginate(request):
            return self.get_paginated_response(serializer.data)
        else:
            return Response(serializer.data, status=200)

    @capable_of('crud_shortlink')
    def post(self, request, academy_id=None):

        serializer = ShortLinkSerializer(data=request.data,
                                         context={
                                             'request': request,
                                             'academy': academy_id
                                         })
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @capable_of('crud_shortlink')
    def put(self, request, short_slug, academy_id=None):

        short = ShortLink.objects.filter(slug=short_slug, academy__id=academy_id).first()
        if short is None:
            raise ValidationException(f'ShortLink {short_slug} not found', slug='short-not-found')

        serializer = ShortLinkSerializer(short,
                                         data=request.data,
                                         context={
                                             'request': request,
                                             'academy': academy_id
                                         })
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @capable_of('crud_shortlink')
    def delete(self, request, academy_id=None):
        # TODO: here i don't add one single delete, because i don't know if it is required
        lookups = self.generate_lookups(request, many_fields=['id'])
        # automation_objects

        if not lookups:
            raise ValidationException('Missing parameters in the querystring', code=400)

        items = ShortLink.objects.filter(**lookups, academy__id=academy_id)
        for i in items:
            utc_now = timezone.now()
            days_ago = i.created_at + timedelta(days=1)
            if days_ago < utc_now:
                raise ValidationException(
                    f'You cannot update or delete short links that have been created more than 1 day ago, create a new link instead',
                    slug='update-days-ago')

        items.delete()

        return Response(None, status=status.HTTP_204_NO_CONTENT)


def get_real_conversion_name(slug):
    mapper = {
        'Website Lead': 'Application Submitted',
    }
    words = re.split(' |_|-', slug)
    words = [w.capitalize() for w in words]
    words = ' '.join(words)
    if words in mapper:
        words = mapper[words]

    return words


def googleads_csv(request):

    ids = request.GET.get('academy', '')
    slugs = request.GET.get('academy_slug', '')

    ids = ids.split(',') if ids else []
    slugs = slugs.split(',') if slugs else []

    if ids:
        form_entries = FormEntry.objects.filter(academy__id__in=ids).order_by('id')

    elif slugs:
        form_entries = FormEntry.objects.filter(academy__slug__in=slugs).order_by('id')

    else:
        form_entries = FormEntry.objects.all()

    if (Academy.objects.filter(id__in=ids).count() != len(ids)
            or Academy.objects.filter(slug__in=slugs).count() != len(slugs)):
        raise ValidationException('Some academy not exist', slug='academy-not-found')

    data = []
    response = HttpResponse(
        content_type='text/csv',
        headers={'Content-Disposition': 'attachment; filename="googleads.csv"'},
    )

    for entry in form_entries:

        if entry.gclid:
            entry_gclid = entry.gclid[-4:]

            if (entry_gclid == '_BwE' and entry.deal_status == 'WON'):
                gclid = entry.gclid
                convertion_name = get_real_conversion_name(entry.tags)

                timezone = pytz.timezone('US/Eastern')
                if entry.won_at is not None:
                    convertion_time = entry.won_at.astimezone(timezone)
                else:
                    convertion_time = entry.updated_at.astimezone(timezone)

                convertion_time = convertion_time.strftime('%Y-%m-%d %H:%M:%S')

                data.append([gclid, convertion_name, convertion_time, None, None])

    writer = csv.writer(response)
    writer.writerow(['Parameters:TimeZone=US/Eastern'])
    writer.writerow(
        ['Google Click ID', 'Conversion Name', 'Conversion Time', 'Conversion Value', 'Conversion Currency'])

    for d in data:
        writer.writerow(d)

    return response
