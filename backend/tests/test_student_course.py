from app.models import User, Course, StudentCourse
import uuid

def test_create_student_course(db_session):
    user = User(
        id=uuid.uuid4(),
        firstname="Test",
        lastname="User",
        username="testuser",
        email="test@example.com",
        hashed_password="hashed",
    )
    db_session.add(user)

    course = Course(
        id=uuid.uuid4(),
        title="Test Course",
        description="For testing"
    )
    db_session.add(course)
    db_session.commit()

    student_course = StudentCourse(student_id=user.id, course_id=course.id)
    db_session.add(student_course)
    db_session.commit()

    result = db_session.query(StudentCourse).filter_by(student_id=user.id).first()
    assert result is not None
    assert result.course_id == course.id
