import serpy
from breathecode.admissions.serializers import GetSmallSpecialtyModeSerializer


class ProfileSmallSerializer(serpy.Serializer):
    """The serializer schema definition."""
    # Use a Field subclass like IntField if you need more validation.
    avatar_url = serpy.Field()


class UserSmallSerializer(serpy.Serializer):
    """The serializer schema definition."""
    # Use a Field subclass like IntField if you need more validation.
    id = serpy.Field()
    first_name = serpy.Field()
    last_name = serpy.Field()
    profile = ProfileSmallSerializer(required=False, many=False)


class AcademyTinySerializer(serpy.Serializer):
    """The serializer schema definition."""
    # Use a Field subclass like IntField if you need more validation.
    id = serpy.Field()
    slug = serpy.Field()
    name = serpy.Field()


class AcademySmallSerializer(serpy.Serializer):
    """The serializer schema definition."""
    # Use a Field subclass like IntField if you need more validation.
    id = serpy.Field()
    slug = serpy.Field()
    name = serpy.Field()
    logo_url = serpy.Field()
    website_url = serpy.Field()


class TinyLayoutDesignSerializer(serpy.Serializer):
    """The serializer schema definition."""
    # Use a Field subclass like IntField if you need more validation.
    slug = serpy.Field()
    name = serpy.Field()
    background_url = serpy.Field()


class LayoutDesignSerializer(serpy.Serializer):
    """The serializer schema definition."""
    # Use a Field subclass like IntField if you need more validation.
    slug = serpy.Field()
    name = serpy.Field()
    is_default = serpy.Field()
    background_url = serpy.Field()
    preview_url = serpy.Field()


class SyllabusVersionSmallSerializer(serpy.Serializer):
    """The serializer schema definition."""
    # Use a Field subclass like IntField if you need more validation.
    version = serpy.Field()
    slug = serpy.MethodField()
    name = serpy.MethodField()
    syllabus = serpy.MethodField()
    duration_in_hours = serpy.MethodField()
    duration_in_days = serpy.MethodField()
    week_hours = serpy.MethodField()

    def get_slug(self, obj):
        return obj.syllabus.slug if obj.syllabus else None

    def get_name(self, obj):
        return obj.syllabus.name if obj.syllabus else None

    def get_syllabus(self, obj):
        return obj.syllabus.id if obj.syllabus else None

    def get_duration_in_hours(self, obj):
        return obj.syllabus.duration_in_hours if obj.syllabus else None

    def get_duration_in_days(self, obj):
        return obj.syllabus.duration_in_days if obj.syllabus else None

    def get_week_hours(self, obj):
        return obj.syllabus.week_hours if obj.syllabus else None


class CohortSmallSerializer(serpy.Serializer):
    """The serializer schema definition."""
    # Use a Field subclass like IntField if you need more validation.
    id = serpy.Field()
    slug = serpy.Field()
    name = serpy.Field()
    specialty_mode = GetSmallSpecialtyModeSerializer(required=False, many=False)
    syllabus_version = SyllabusVersionSmallSerializer(required=False, many=False)


class CohortMidSerializer(serpy.Serializer):
    """The serializer schema definition."""
    # Use a Field subclass like IntField if you need more validation.
    id = serpy.Field()
    slug = serpy.Field()
    name = serpy.Field()
    kickoff_date = serpy.Field()
    ending_date = serpy.Field()
    specialty_mode = GetSmallSpecialtyModeSerializer(required=False, many=False)
    syllabus_version = SyllabusVersionSmallSerializer(required=False, many=False)


class SpecialtySerializer(serpy.Serializer):
    """The serializer schema definition."""
    # Use a Field subclass like IntField if you need more validation.
    id = serpy.Field()
    slug = serpy.Field()
    name = serpy.Field()
    logo_url = serpy.Field()
    description = serpy.Field()

    updated_at = serpy.Field()
    created_at = serpy.Field()


class BadgeSmallSerializer(serpy.Serializer):
    """The serializer schema definition."""
    # Use a Field subclass like IntField if you need more validation.
    id = serpy.Field()
    name = serpy.Field()


class BadgeSerializer(serpy.Serializer):
    """The serializer schema definition."""
    # Use a Field subclass like IntField if you need more validation.
    id = serpy.Field()
    slug = serpy.Field()
    name = serpy.Field()
    logo_url = serpy.Field()


class UserSpecialtySerializer(serpy.Serializer):
    """The serializer schema definition."""
    # Use a Field subclass like IntField if you need more validation.
    id = serpy.Field()
    signed_by = serpy.Field()
    signed_by_role = serpy.Field()
    status = serpy.Field()
    status_text = serpy.Field()
    user = UserSmallSerializer(many=False)
    specialty = SpecialtySerializer(many=False)
    academy = AcademySmallSerializer(many=False)
    cohort = CohortMidSerializer(required=False, many=False)

    preview_url = serpy.Field()

    layout = TinyLayoutDesignSerializer(required=False, many=False)

    expires_at = serpy.Field()
    updated_at = serpy.Field()
    created_at = serpy.Field()
