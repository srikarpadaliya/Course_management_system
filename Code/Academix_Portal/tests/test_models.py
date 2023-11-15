from django.test import TestCase
from django.contrib.auth.models import User

from Academix_Portal.models import student_profile,faculty_profile,Course
from Academix_Portal.models import Assignment,Submission
from django.db.utils import IntegrityError
from datetime import datetime
## Notes for people involved in testing ##

"""
1. class name should start with 'Test'.
2. testing function name should start with 'test_'
3. instance creation name should always be SetUp
4. if you are creating any files under tests folder, make sure the filename is starting with test as django looks for test under test folder

5. for running test use python manage.py test Academix_Portal
6. Save the console output in textfile. few sample test case are provided 3 of them are true and one is wrong
   in line 82. 1 != 2 since in line 80, i have added only 1 course i.e Computer Science 101 to faculty aakash.
   (you can read console output sample in model_test.txt)

"""

""" Current test cases contains 5 models: student_profile , faculty_profile , Course , Assignment, Submission """

from django.test import TestCase
from django.contrib.auth.models import User
from Academix_Portal.models import student_profile, faculty_profile, Course

class TestModels(TestCase):
    def setUp(self):
        self.user_student = User.objects.create_user(username='shrikar', password='shrikar123')
        self.user_faculty = User.objects.create_user(username='aakash', password='aakash123')

        self.faculty = faculty_profile.objects.create(
            user=self.user_faculty,
            first_name='aakash',
            middle_name='xyz',
            last_name='patel'
        )

        self.student = student_profile.objects.create(
            user=self.user_student,
            first_name='shrikar',
            middle_name='shaileshbhai',
            last_name='padaliya',
            batch=2022,
            branch='ICT',
            program='B.Tech'
        )

        self.course = Course.objects.create(
            name='Computer Science 101',
            course_code='CS101',
            description='Introduction to Computer Science',
            faculty=self.faculty
        )
           # creating an assignment here
        self.assignment = Assignment.objects.create(
            name='Assignment 1',
            description='First assignment',
            duedate=datetime(2023, 12, 1, 0, 0, 0),
            max_grade=100,
            attachment='aakash_assignment1',
            assignment_course=self.course
        )

        # creating a student submission
        self.submission = Submission.objects.create(
            student=self.student,
            graded=False,
            grade=None,
            work='shrikar_work1',
            feedback='Good work!',
            assignment=self.assignment
        )

    def test_duplicate_usernames(self):
        # Test for uniqueness of usernames
        user_duplicate = User(username='shrikar', password='testpassword')
        with self.assertRaises(Exception):
            user_duplicate.save()

    def test_student_enroll_in_course(self):
        # Test if a student can enroll in a course
        self.course.studentlist.add(self.student)
        self.assertEqual(self.course.studentlist.count(), 1)

    def test_course_with_no_faculty(self):
        # Test creating a course without a faculty
        
        with self.assertRaises(IntegrityError):
            course_no_faculty = Course.objects.create(
            name='No Faculty Course',
            course_code='NF101',
            description='Course without faculty'
        )

    def test_course_without_students(self):
        # Test creating a course without students
        course_empty = Course.objects.create(
            name='Empty Course',
            course_code='EC101',
            description='Course with no students',
            faculty=self.faculty
        )
        self.assertEqual(course_empty.studentlist.count(), 0)

    def test_student_courses_relationship(self):
        # Testing relationship between student and courses
        self.student.student_courses.add(self.course)
        self.assertEqual(self.student.student_courses.count(), 1)
        self.assertEqual(self.student.student_courses.first().name, 'Computer Science 101')

    def test_faculty_courses_relationship(self):
        # Testing relationship between faculty and courses
        self.faculty.faculty_courses.add(self.course)
        self.assertEqual(self.faculty.faculty_courses.count(), 1)
        self.assertEqual(self.faculty.faculty_courses.first().name, 'Computer Science 101')

    def test_course_students_and_faculty(self):
        # Testing that a course has both students and a faculty
        self.course.studentlist.add(self.student)
        self.assertEqual(self.course.studentlist.count(), 1)
        self.assertEqual(self.course.faculty, self.faculty)

    def test_student_str_method(self):
        
        self.assertEqual(str(self.student), 'shrikar')

    def test_faculty_str_method(self):
        
        self.assertEqual(str(self.faculty), 'aakash')

    def test_course_str_method(self):
        
        self.assertEqual(str(self.course), 'Computer Science 101')


    def test_assignment_str_method(self):
        # Test the __str__ method of Assignment
        self.assertEqual(str(self.assignment), 'Assignment 1')

    def test_submission_str_method(self):
        # Test the __str__ method of Submission
        expected_str = f'{self.assignment.assignment_course.course_code} shrikarpadaliya'
        self.assertEqual(str(self.submission), expected_str)

    def test_submission_defaults(self):
        # Test submission default values
        # Create a new assignment to avoid unique constraint violation
        new_assignment = Assignment.objects.create(
            name='Assignment 2',
            description='Second assignment',
            duedate=datetime(2023, 12, 2, 0, 0, 0),
            max_grade=90,
            attachment='http://example.com/assignment2',
            assignment_course=self.course
        )
        # Use a different student to avoid unique constraint violation
        new_student = student_profile.objects.create(
            user=User.objects.create_user(username='mustafa', password='mustafa123'),
            first_name='mustafa',
            last_name='lokhandwala',
            batch=2022,
            branch='CSE',
            program='B.Tech'
        )

        submission_defaults = Submission(student=new_student, assignment=new_assignment)
        submission_defaults.save()
        self.assertFalse(submission_defaults.graded)
        self.assertIsNone(submission_defaults.grade)
        self.assertIsNone(submission_defaults.feedback)
        self.assertIsNotNone(submission_defaults.timestamp)  # Ensure timestamp is not None

    def test_assignment_due_date(self):
        # Test assignment due date
        self.assertEqual(self.assignment.duedate, datetime(2023, 12, 1, 0, 0, 0))

    def test_submission_timestamp_auto_now_add(self):
        # Test that the timestamp in Submission is set automatically on creation
        new_assignment = Assignment.objects.create(
            name='Assignment 2',
            description='Second assignment',
            duedate=datetime(2023, 12, 2, 0, 0, 0),
            max_grade=90,
            attachment='http://example.com/assignment2',
            assignment_course=self.course
        )
        # Use a different student to avoid unique constraint violation
        new_student = student_profile.objects.create(
            user=User.objects.create_user(username='mustafa', password='mustafa123'),
            first_name='mustafa',
            last_name='lokhandwala',
            batch=2022,
            branch='CSE',
            program='B.Tech'
        )
        submission_timestamp = Submission.objects.create(
            student=new_student,
            graded=False,
            grade=None,
            work='shrikar_work',
            feedback='Great job!',
            assignment=new_assignment
        )
        self.assertIsNotNone(submission_timestamp.timestamp)

    def test_submission_grade_update(self):
        # Testing updating the grade in Submission
        updated_grade = 95
        self.submission.grade = updated_grade
        self.submission.save()
        self.assertEqual(Submission.objects.get(id=self.submission.id).grade, updated_grade)

    def test_submission_feedback_update(self):
        # Testing updating the feedback in Submission
        updated_feedback = 'Excellent work!'
        self.submission.feedback = updated_feedback
        self.submission.save()
        self.assertEqual(Submission.objects.get(id=self.submission.id).feedback, updated_feedback)

    def test_assignment_course_relationship(self):
        # Testing relationship between Assignment and Course
        self.assertEqual(self.assignment.assignment_course, self.course)

    def test_submission_assignment_relationship(self):
        # Testing relationship between Submission and Assignment
        self.assertEqual(self.submission.assignment, self.assignment)

    def test_assignment_submission_relationship(self):
        # Testing relationship between Assignment and Submission
        assignment_submissions = self.assignment.submission_set.all()
        self.assertEqual(assignment_submissions.count(), 1)
        self.assertEqual(assignment_submissions.first(), self.submission)

    def test_duplicate_assignment_name(self):
        # Testing for uniqueness of assignment names within a course
        Assignment.objects.create(
            name='Assignment temp',
            description='First assignment',
            duedate=datetime(2023, 12, 1, 0, 0, 0),
            max_grade=100,
            attachment='aakash_assignment1',
            assignment_course=self.course
        )

        with self.assertRaises(IntegrityError):
            Assignment.objects.create(
                name='Assignment temp',
                description='Duplicate assignment name',
                duedate=datetime(2023, 12, 2, 0, 0, 0),
                max_grade=90,
                attachment='aakash_assignment1',
                assignment_course=self.course
            )

    def test_submission_student_assignment_uniqueness(self):
        # Testing for uniqueness of submissions by student for a specific assignment
        assignment = Assignment.objects.create(
            name='Assignment 2',
            description='Second assignment',
            duedate=datetime(2023, 12, 2, 0, 0, 0),
            max_grade=90,
            attachment='aakash_assignment2',
            assignment_course=self.course
        )
        Submission.objects.create(
            student=self.student,
            graded=False,
            grade=None,
            work='shrikar_work2',
            feedback='Good work!',
            assignment=assignment
        )
        with self.assertRaises(IntegrityError):
            Submission.objects.create(
                student=self.student,
                graded=False,
                grade=None,
                work='shrikar_work2',
                feedback='Another submission',
                assignment=assignment
            )

    def test_assignment_course_foreign_key_constraint(self):
        # Testing integrity constraint for assignment_course foreign key
        with self.assertRaises(IntegrityError):
            Assignment.objects.create(
                name='Assignment 3',
                description='Third assignment',
                duedate=datetime(2023, 12, 3, 0, 0, 0),
                max_grade=80,
                attachment='aakash_assignment3',
                assignment_course=None
            )

    def test_submission_assignment_foreign_key_constraint(self):
        # Testing integrity constraint for submission assignment foreign key
        with self.assertRaises(IntegrityError):
            Submission.objects.create(
                student=self.student,
                graded=False,
                grade=None,
                work='http://example.com/submission3',
                feedback='Yet another submission',
                assignment=None
            )