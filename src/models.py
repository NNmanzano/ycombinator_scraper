"""
Data shapes shared across the pipeline. Plain dataclasses, no ORM, no
validation framework, this is a scraper writing to an Excel file.
"""
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Founder:
    name: str
    role: str
    linkedin_url: Optional[str] = None


@dataclass
class Company:
    slug: str
    name: str
    website: str
    founders: list[Founder] = field(default_factory=list)
    scrape_error: Optional[str] = None

    @property
    def ceo(self) -> Optional[Founder]:
        for founder in self.founders:
            if "ceo" in founder.role.lower():
                return founder
        return self.founders[0] if self.founders else None

    def to_row(self) -> dict:
        ceo = self.ceo
        return {
            "Company name": self.name,
            "Website": self.website,
            "YC Slug": self.slug,
            "CEO Name": ceo.name if ceo else "",
            "CEO LinkedIn": ceo.linkedin_url if ceo else "",
            "All Founders": "; ".join(f"{f.name} ({f.role})" for f in self.founders),
            "Scrape Error": self.scrape_error or "",
        }
