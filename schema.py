# Domain: Job Posts
# Purpose: Define and validate extracted job information

# 1. IMPORT REQUIRED LIBRARIES

# BaseModel helps us create a Pydantic data model.
# Field allows us to define default values and descriptions.
# Imports components from Pydantic

from pydantic import BaseModel, Field


# 2. CREATE THE PYDANTIC MODEL

# Extracted is the model name required by the assignment.
# It inherits validation features from BaseModel.
# Each field represents information from a job advertisement.

class Extracted(BaseModel):

    # Store the advertised job title.
    job_title: str | None = Field(
        default=None,
        description="The title of the advertised job"
    )

    # Store the name of the hiring company.
    company: str | None = Field(
        default=None,
        description="The name of the hiring company"
    )

    # Store the city, country, or remote job location.
    location: str | None = Field(
        default=None,
        description="The location of the job"
    )

    # Store the salary or salary range mentioned in the text.
    salary: str | None = Field(
        default=None,
        description="The advertised salary or salary range"
    )

    # Store the required work experience.
    experience: str | None = Field(
        default=None,
        description="The required work experience"
    )

    # Store the employment type, such as full-time or part-time.
    employment_type: str | None = Field(
        default=None,
        description="The type of employment"
    )

    # Store the last date for submitting an application.
    application_deadline: str | None = Field(
        default=None,
        description="The deadline for applying"
    )

    # Store the application link if it is available.
    application_url: str | None = Field(
        default=None,
        description="The application link if provided"
    )
