"""
Base serializers and utilities
"""


class CurrentPKURLDefault:
    """
    Custom default class to get primary key from URL context
    Used in serializers to automatically extract PK from view kwargs

    Example:
        project_id = serializers.IntegerField(
            default=CurrentPKURLDefault(),
            required=False
        )
    """

    requires_context = True

    def __call__(self, serializer_field):
        """
        Extract PK from view kwargs in serializer context
        """
        view = serializer_field.context.get("view")
        if view and hasattr(view, "kwargs"):
            return view.kwargs.get("pk")
        return None

    def __repr__(self):
        return f"{self.__class__.__name__}()"
