"""Utility functions for repcal."""


def ordinal(n: int) -> str:
    """Convert a number to its ordinal representation.

    Args:
        n: Integer to convert (e.g., 1, 2, 3, 21, 22, 23)

    Returns:
        String with ordinal suffix (e.g., '1st', '2nd', '3rd', '21st', '22nd', '23rd')

    Examples:
        >>> ordinal(1)
        '1st'
        >>> ordinal(22)
        '22nd'
        >>> ordinal(13)
        '13th'
    """
    return f"{n}{['th', 'st', 'nd', 'rd'][((n//10%10!=1)*(n%10<4)*n%10)::4][0]}"
