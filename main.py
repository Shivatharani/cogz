from fastapi import FastAPI, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from database import engine, Base, get_db
from models import Course, Student, Enrollment
from schemas import (
    CourseCreate,
    CourseUpdate,
    CourseResponse,
    StudentCreate,
    StudentResponse,
    EnrollmentCreate,
    EnrollmentResponse
)


app = FastAPI(

    title="Course Management API",

    description="FastAPI Backend for Digital Nurture",

    version="1.0",

    contact={

        "name": "Shivatharani",

        "email": "admin@gmail.com"

    }

)


# ROOT ENDPOINT

@app.get("/")

async def root():

    return {

        "message": "API running"

    }


# CREATE TABLES

@app.on_event("startup")

async def startup():

    async with engine.begin() as conn:

        await conn.run_sync(

            Base.metadata.create_all

        )


# BACKGROUND TASK

def send_confirmation_email(email: str):

    print(f"Sending confirmation to {email}")


# ==========================
# COURSE APIs
# ==========================


@app.post(

    "/api/courses/",

    response_model=CourseResponse,

    status_code=status.HTTP_201_CREATED,

    tags=["Courses"],

    summary="Create Course",

    response_description="Course Created Successfully"

)

async def create_course(

    course: CourseCreate,

    db: AsyncSession = Depends(get_db)

):

    new_course = Course(

        name=course.name,

        code=course.code,

        credits=course.credits,

        department_id=course.department_id

    )

    db.add(new_course)

    await db.commit()

    await db.refresh(new_course)

    return new_course


@app.get(

    "/api/courses/",

    response_model=list[CourseResponse],

    tags=["Courses"]

)

async def get_courses(

    skip: int = 0,

    limit: int = 10,

    department_id: int | None = None,

    db: AsyncSession = Depends(get_db)

):

    query = select(Course)

    if department_id:

        query = query.where(

            Course.department_id == department_id

        )

    query = query.offset(skip).limit(limit)

    result = await db.execute(query)

    return result.scalars().all()


@app.get(

    "/api/courses/{course_id}",

    response_model=CourseResponse,

    tags=["Courses"]

)

async def get_course(

    course_id: int,

    db: AsyncSession = Depends(get_db)

):

    result = await db.execute(

        select(Course).where(

            Course.id == course_id

        )

    )

    course = result.scalar_one_or_none()

    if course is None:

        raise HTTPException(

            status_code=404,

            detail="Course not found"

        )

    return course


@app.put(

    "/api/courses/{course_id}",

    response_model=CourseResponse,

    tags=["Courses"]

)

async def update_course(

    course_id: int,

    data: CourseUpdate,

    db: AsyncSession = Depends(get_db)

):

    result = await db.execute(

        select(Course).where(

            Course.id == course_id

        )

    )

    course = result.scalar_one_or_none()

    if course is None:

        raise HTTPException(

            status_code=404,

            detail="Course not found"

        )

    if data.name is not None:

        course.name = data.name

    if data.code is not None:

        course.code = data.code

    if data.credits is not None:

        course.credits = data.credits

    if data.department_id is not None:

        course.department_id = data.department_id

    await db.commit()

    await db.refresh(course)

    return course


@app.delete(

    "/api/courses/{course_id}",

    status_code=status.HTTP_204_NO_CONTENT,

    tags=["Courses"]

)

async def delete_course(

    course_id: int,

    db: AsyncSession = Depends(get_db)

):

    result = await db.execute(

        select(Course).where(

            Course.id == course_id

        )

    )

    course = result.scalar_one_or_none()

    if course is None:

        raise HTTPException(

            status_code=404,

            detail="Course not found"

        )

    await db.delete(course)

    await db.commit()

    return


# ==========================
# STUDENT APIs
# ==========================


@app.post(

    "/api/students/",

    response_model=StudentResponse,

    status_code=201,

    tags=["Students"]

)

async def create_student(

    student: StudentCreate,

    db: AsyncSession = Depends(get_db)

):

    new_student = Student(

        first_name=student.first_name,

        last_name=student.last_name,

        email=student.email

    )

    db.add(new_student)

    await db.commit()

    await db.refresh(new_student)

    return new_student



@app.get(

    "/api/students/",

    response_model=list[StudentResponse],

    tags=["Students"]

)

async def get_students(

    db: AsyncSession = Depends(get_db)

):

    result = await db.execute(

        select(Student)

    )

    return result.scalars().all()


# ==========================
# ENROLLMENT APIs
# ==========================


@app.post(

    "/api/enrollments/",

    response_model=EnrollmentResponse,

    status_code=201,

    tags=["Enrollments"]

)

async def create_enrollment(

    enrollment: EnrollmentCreate,

    background_tasks: BackgroundTasks,

    db: AsyncSession = Depends(get_db)

):

    new_enrollment = Enrollment(

        student_id=enrollment.student_id,

        course_id=enrollment.course_id

    )

    db.add(new_enrollment)

    await db.commit()

    await db.refresh(new_enrollment)


    student = await db.get(

        Student,

        enrollment.student_id

    )

    if student:

        background_tasks.add_task(

            send_confirmation_email,

            student.email

        )

    return new_enrollment



@app.get(

    "/api/enrollments/",

    response_model=list[EnrollmentResponse],

    tags=["Enrollments"]

)

async def get_enrollments(

    db: AsyncSession = Depends(get_db)

):

    result = await db.execute(

        select(Enrollment)

    )

    return result.scalars().all()


# ==========================
# COURSE -> STUDENTS
# ==========================


@app.get(

    "/api/courses/{course_id}/students/",

    response_model=list[StudentResponse],

    tags=["Courses"]

)

async def get_course_students(

    course_id: int,

    db: AsyncSession = Depends(get_db)

):

    result = await db.execute(

        select(Student)

        .join(

            Enrollment,

            Student.id == Enrollment.student_id

        )

        .where(

            Enrollment.course_id == course_id

        )

    )

    return result.scalars().all()

