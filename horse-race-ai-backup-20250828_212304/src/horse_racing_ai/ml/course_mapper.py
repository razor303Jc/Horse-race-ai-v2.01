#!/usr/bin/env python3
"""
Course Mapping System for Horse Racing ML Models
===============================================

Provides consistent numerical mapping for racecourses across the system.
New courses can be added here and will be automatically picked up by ML models.
"""

from typing import Dict, Optional


class CourseMapper:
    """Maps racecourse names to numerical values for ML models."""

    # Core UK racecourses mapping
    COURSE_MAPPING = {
        # Major flat courses
        "newmarket": 1,
        "ascot": 2,
        "epsom": 3,
        "goodwood": 4,
        "york": 5,
        "doncaster": 6,
        "newbury": 7,
        "sandown": 8,
        "kempton": 9,
        "lingfield": 10,
        "wolverhampton": 11,
        "southwell": 12,
        "chelmsford": 13,
        "leicester": 14,
        "nottingham": 15,
        "yarmouth": 16,
        "windsor": 17,
        "salisbury": 18,
        "chester": 19,
        "haydock": 20,
        "redcar": 21,
        "ripon": 22,
        "thirsk": 23,
        "pontefract": 24,
        "catterick": 25,
        "hamilton": 26,
        "musselburgh": 27,
        "ayr": 28,
        "carlisle": 29,
        "hexham": 30,
        # Jump racing courses
        "cheltenham": 31,
        "aintree": 32,
        "kempton park": 33,
        "sandown park": 34,
        "newbury racecourse": 35,
        "ascot racecourse": 36,
        "doncaster racecourse": 37,
        "york racecourse": 38,
        "haydock park": 39,
        "chepstow": 40,
        "ludlow": 41,
        "worcester": 42,
        "stratford": 43,
        "warwick": 44,
        "uttoxeter": 45,
        "market rasen": 46,
        "huntingdon": 47,
        "fakenham": 48,
        "fontwell": 49,
        "plumpton": 50,
        "newton abbot": 51,
        "exeter": 52,
        "taunton": 53,
        "wincanton": 54,
        "ffos las": 55,
        "bangor": 56,
        "sedgefield": 57,
        "wetherby": 58,
        "kelso": 59,
        "perth": 60,
        # Irish courses
        "curragh": 61,
        "leopardstown": 62,
        "fairyhouse": 63,
        "punchestown": 64,
        "gowran park": 65,
        "naas": 66,
        "navan": 67,
        "cork": 68,
        "tipperary": 69,
        "killarney": 70,
        "galway": 71,
        "bellewstown": 72,
        "laytown": 73,
        "roscommon": 74,
        "sligo": 75,
        "downpatrick": 76,
        "down royal": 77,
        # All-weather courses
        "dundalk": 78,
        "kempton aw": 79,
        "lingfield aw": 80,
        "wolverhampton aw": 81,
        "southwell aw": 82,
        "chelmsford city": 83,
        "newcastle": 84,
        "brighton": 85,
        "bath": 86,
        "folkestone": 87,
        "ffos las aw": 88,
        # International courses (for future expansion)
        "meydan": 100,
        "sha tin": 101,
        "tokyo": 102,
        "longchamp": 103,
        "chantilly": 104,
        "deauville": 105,
        "cologne": 106,
        "baden-baden": 107,
        "milan": 108,
        "rome": 109,
        "belmont park": 110,
        "saratoga": 111,
        "churchill downs": 112,
        "keeneland": 113,
        "santa anita": 114,
        "del mar": 115,
        "woodbine": 116,
        "flemington": 117,
        "randwick": 118,
        "moonee valley": 119,
        "caulfield": 120,
        # Default for unknown courses
        "unknown": 999,
    }

    @classmethod
    def get_course_id(cls, course_name: str) -> int:
        """
        Get numerical ID for a course name.

        Args:
            course_name: Name of the racecourse

        Returns:
            Numerical ID for the course, or 999 for unknown courses
        """
        if not course_name:
            return cls.COURSE_MAPPING["unknown"]

        # Normalize course name
        normalized = course_name.lower().strip()

        # Direct lookup
        if normalized in cls.COURSE_MAPPING:
            return cls.COURSE_MAPPING[normalized]

        # Try partial matches for common variations
        for course, course_id in cls.COURSE_MAPPING.items():
            if course in normalized or normalized in course:
                return course_id

        # If not found, return unknown
        print(f"Warning: Unknown course '{course_name}' mapped to ID 999")
        return cls.COURSE_MAPPING["unknown"]

    @classmethod
    def get_course_name(cls, course_id: int) -> Optional[str]:
        """
        Get course name from numerical ID.

        Args:
            course_id: Numerical ID of the course

        Returns:
            Course name or None if not found
        """
        for course_name, cid in cls.COURSE_MAPPING.items():
            if cid == course_id:
                return course_name
        return None

    @classmethod
    def add_course(cls, course_name: str, course_id: Optional[int] = None) -> int:
        """
        Add a new course to the mapping.

        Args:
            course_name: Name of the new course
            course_id: Optional specific ID, otherwise auto-assigned

        Returns:
            The assigned course ID
        """
        normalized = course_name.lower().strip()

        # Check if course already exists
        if normalized in cls.COURSE_MAPPING:
            return cls.COURSE_MAPPING[normalized]

        # Auto-assign ID if not provided
        if course_id is None:
            # Find next available ID
            used_ids = set(cls.COURSE_MAPPING.values())
            course_id = 1
            while course_id in used_ids:
                course_id += 1

        # Add to mapping
        cls.COURSE_MAPPING[normalized] = course_id
        print(f"Added new course: '{course_name}' -> ID {course_id}")

        return course_id

    @classmethod
    def get_all_courses(cls) -> Dict[str, int]:
        """Get all course mappings."""
        return cls.COURSE_MAPPING.copy()

    @classmethod
    def get_course_stats(cls) -> Dict[str, int]:
        """Get statistics about course mappings."""
        return {
            "total_courses": len(cls.COURSE_MAPPING),
            "uk_courses": len(
                [c for c in cls.COURSE_MAPPING.keys() if cls.COURSE_MAPPING[c] < 100]
            ),
            "international_courses": len(
                [
                    c
                    for c in cls.COURSE_MAPPING.keys()
                    if 100 <= cls.COURSE_MAPPING[c] < 999
                ]
            ),
            "max_id": max(cls.COURSE_MAPPING.values()),
        }


# Convenience functions for easy import
def map_course(course_name: str) -> int:
    """Map a course name to numerical ID."""
    return CourseMapper.get_course_id(course_name)


def get_course_name(course_id: int) -> Optional[str]:
    """Get course name from ID."""
    return CourseMapper.get_course_name(course_id)


def add_new_course(course_name: str, course_id: Optional[int] = None) -> int:
    """Add a new course to the mapping."""
    return CourseMapper.add_course(course_name, course_id)


if __name__ == "__main__":
    # Test the course mapping
    print("Course Mapping System Test")
    print("=" * 30)

    # Test some common courses
    test_courses = ["Newmarket", "ascot", "EPSOM", "goodwood", "unknown_course"]

    for course in test_courses:
        course_id = map_course(course)
        print(f"{course:15} -> ID {course_id}")

    print("\nCourse Statistics:")
    stats = CourseMapper.get_course_stats()
    for key, value in stats.items():
        print(f"{key:20}: {value}")

    print(f"\nTotal mapped courses: {len(CourseMapper.get_all_courses())}")
