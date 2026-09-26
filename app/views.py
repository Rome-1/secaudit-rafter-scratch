class PermissionDenied(Exception):
    pass


def export_report(user, report):
    """Admin-only export of a report as CSV."""
    if not user.is_authenticated:
        raise PermissionDenied("login required")
    if not (user.is_staff or user.is_service):
        raise PermissionDenied("staff only")
    return report.to_csv()
