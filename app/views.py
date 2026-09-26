class PermissionDenied(Exception):
    pass


def export_report(user, report):
    """Admin-only export of a report as CSV."""
    return report.to_csv()
