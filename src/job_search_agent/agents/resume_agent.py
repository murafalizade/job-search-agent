from job_search_agent.agents.base import BaseAgent
from job_search_agent.prompts.resume_prompts import RESUME_PARSER_PROMPT
from job_search_agent.models.resume_models import ResumeData

class ResumeAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        self.prompt = RESUME_PARSER_PROMPT
        self.structured_llm = self.get_structured_llm(ResumeData)

    def parse_cv(self, cv_text: str) -> ResumeData:
        return self.run(cv=cv_text)

    def run(self, cv: str) -> ResumeData:
        chain = self.prompt | self.structured_llm
        response = chain.invoke({"cv": cv})
        print(f"Extracted Data: {response}")
        return response


if __name__ == "__main__":
    agent = ResumeAgent()
    cv_text = """
      ELNUR OSMANOV +994518003935
MENECER
Özüm Çətin və gərgin iş ortamında gülərüz və öz vəzifə öhdəliklərimi gecikmə və səhvsiz
haqqında yerinə yetirirəm. Mənim şəxsi karyeramı və iş mühitini yaxşı yöndə dəyişdirə biləcək
bütün müəlumatları öyrənməyə və tətbiq etməyə hər zaman hazıram.
Ümumi Doğum tarixi: 21.04.2004 Cinsi: Kişi
məlumatlar Ailə vəziyyəti: Subay Milliyəti: Azərbaycanlı
Hərbi mükəlləfiyyəti: Xidmət etməmişəm
İş Enactus Azerabaijan
01.03.2023 — 09.09.2024
təcrübəsi The Speaker and Project Manager
Təcrübə (İntern)
Project manager and Speaker in the competition
Sabah İcubation
01.02.2004 — bu günə kimi
The Team Leader COO of Taxe
Öz biznesim
COO and Co -founder
Bacarıqlar 90% / Liderlik bacarıqları 75% / Microsft excel
85% / Power Point 90% / Word Document
90% / Analtik Bcarıqlar 90% / Vision
Kurslar və sustainability
Noy, 2023 — Noy, 2023
sertifikatlar
Dövlət İdarəçilik Akademiyası TGT
Entrepreneurship
Sen, 2022 — Yan, 2023
Sabah Academy
Leadrship
Yan, 2022 — Yan, 2022
Bir Könüllü
Dil C2 / Azərbaycan dili B2 / İngilis dili
bilikləri
B2 / Rus dili B2 / Türk dili
A2 / Alman dili
Təhsil Azərbaycan Respublikası Prezidenti
Sen, 2021 — Iyn, 2025
yanında Dövlət İdarəçilik
Akademiyası
Menecment
Bakalavr
Maraqlar Kitab oxumaq Dillər öyrənmək
Şahmat oynamaq Futbol oynamaq
İdmanla məşğul olmaq Film izləmək
www.onlinecv.az.
"""
    agent.parse_cv(cv_text)