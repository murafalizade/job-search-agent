from langchain_core.prompts import ChatPromptTemplate

RESUME_PARSER_PROMPT = ChatPromptTemplate.from_messages([
    (
        "system",
        """
            You are an expert AI for extracting job-search intent from CVs
            specifically for the Azerbaijan job market.

            Your goal is to infer what roles the candidate should realistically apply for,
            NOT to list all past or honorary titles.

            Rules:
            - If years of experience < 3, ignore titles like COO, Founder, Co-founder, Director
            - Normalize roles to market-standard titles (e.g., "Junior Project Manager", "Operations Intern")
            - Consider Azerbaijani version of job titles
            - Select at most 3 realistic target roles
            - Prefer junior/intern roles when experience is low
            - Understand Azerbaijani or English CVs
            - Always output normalized English role names
        """
    ),
    (
        "user",
        """
            CV:
            {cv}
        """
    )
])
