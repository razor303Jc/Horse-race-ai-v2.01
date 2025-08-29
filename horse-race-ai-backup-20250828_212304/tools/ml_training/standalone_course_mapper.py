#!/usr/bin/env python3
"""
Standalone Course Mapper for ML Training
========================================

Simple course mapping functionality for ML containers without dependencies.
"""


class StandaloneCourseMapper:
    """Simple course mapper without external dependencies."""

    COURSE_MAPPING = {
        # UK Flat Racing Courses
        "Newmarket": 1,
        "Ascot": 2,
        "Goodwood": 3,
        "York": 4,
        "Epsom": 5,
        "Doncaster": 6,
        "Chester": 7,
        "Sandown": 8,
        "Kempton": 9,
        "Lingfield": 10,
        "Windsor": 11,
        "Newbury": 12,
        "Salisbury": 13,
        "Bath": 14,
        "Brighton": 15,
        "Carlisle": 16,
        "Catterick": 17,
        "Chepstow": 18,
        "Exeter": 19,
        "Ffos Las": 20,
        "Folkestone": 21,
        "Hamilton": 22,
        "Haydock": 23,
        "Hereford": 24,
        "Leicester": 25,
        "Musselburgh": 26,
        "Nottingham": 27,
        "Pontefract": 28,
        "Redcar": 29,
        "Ripon": 30,
        "Southwell": 31,
        "Thirsk": 32,
        "Warwick": 33,
        "Wolverhampton": 34,
        "Yarmouth": 35,
        # UK Jump Racing Courses
        "Cheltenham": 36,
        "Aintree": 37,
        "Huntingdon": 38,
        "Market Rasen": 39,
        "Newton Abbot": 40,
        "Plumpton": 41,
        "Stratford": 42,
        "Taunton": 43,
        "Uttoxeter": 44,
        "Wincanton": 45,
        "Worcester": 46,
        "Fakenham": 47,
        "Fontwell": 48,
        "Ludlow": 49,
        "Perth": 50,
        "Sedgefield": 51,
        "Towcester": 52,
        "Wetherby": 53,
        "Hexham": 54,
        "Kelso": 55,
        "Ayr": 56,
        "Bangor": 57,
        "Devon": 58,
        # Irish Courses
        "The Curragh": 61,
        "Leopardstown": 62,
        "Fairyhouse": 63,
        "Punchestown": 64,
        "Gowran Park": 65,
        "Cork": 66,
        "Galway": 67,
        "Naas": 68,
        "Navan": 69,
        "Tipperary": 70,
        "Thurles": 71,
        "Killarney": 72,
        "Limerick": 73,
        "Clonmel": 74,
        "Downpatrick": 75,
        "Down Royal": 76,
        "Bellewstown": 77,
        "Dundalk": 78,
        "Listowel": 79,
        "Roscommon": 80,
        "Sligo": 81,
        "Tramore": 82,
        "Wexford": 83,
        "Ballinrobe": 84,
        "Kilbeggan": 85,
        "Laytown": 86,
        # International Major Courses
        "Churchill Downs": 87,
        "Belmont Park": 88,
        "Saratoga": 89,
        "Santa Anita": 90,
        "Del Mar": 91,
        "Keeneland": 92,
        "Gulfstream Park": 93,
        "Woodbine": 94,
        "Longchamp": 95,
        "Chantilly": 96,
        "Deauville": 97,
        "Saint-Cloud": 98,
        "Cologne": 99,
        "Baden-Baden": 100,
        "Tokyo": 101,
        "Nakayama": 102,
        "Flemington": 103,
        "Randwick": 104,
        "Caulfield": 105,
        "Rosehill": 106,
        "Moonee Valley": 107,
        "Sha Tin": 108,
        "Happy Valley": 109,
        "Meydan": 110,
    }

    @classmethod
    def get_course_id(cls, course_name: str) -> int:
        """
        Get numerical ID for a racecourse.

        Args:
            course_name: Name of the racecourse

        Returns:
            Numerical ID for the course (999 for unknown courses)
        """
        if not course_name:
            return 999

        # Clean course name
        clean_name = course_name.strip()

        # Direct lookup
        if clean_name in cls.COURSE_MAPPING:
            return cls.COURSE_MAPPING[clean_name]

        # Case-insensitive lookup
        for course, course_id in cls.COURSE_MAPPING.items():
            if course.lower() == clean_name.lower():
                return course_id

        # Partial match lookup
        clean_lower = clean_name.lower()
        for course, course_id in cls.COURSE_MAPPING.items():
            if clean_lower in course.lower() or course.lower() in clean_lower:
                return course_id

        # Unknown course
        return 999

    @classmethod
    def get_course_count(cls) -> int:
        """Get total number of mapped courses."""
        return len(cls.COURSE_MAPPING)

    @classmethod
    def list_courses(cls) -> list:
        """List all mapped courses."""
        return list(cls.COURSE_MAPPING.keys())


def test_course_mapper():
    """Test the course mapper functionality."""
    mapper = StandaloneCourseMapper()

    test_courses = [
        "Newmarket",
        "Ascot",
        "newmarket",  # lowercase
        "ASCOT",  # uppercase
        "Unknown Course",  # should return 999
        None,  # should return 999
        "",  # should return 999
    ]

    print("🏁 Testing Course Mapper:")
    for course in test_courses:
        course_id = mapper.get_course_id(course)
        print(f"   {course} -> {course_id}")

    print(f"\n📊 Total mapped courses: {mapper.get_course_count()}")


if __name__ == "__main__":
    test_course_mapper()
