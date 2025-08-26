from neo4j import GraphDatabase
import json
from typing import Dict, Any, List

class Neo4jMemoryManager:
    def __init__(self):
        self.driver = GraphDatabase.driver(
            "neo4j://127.0.0.1:7687", 
            auth=("neo4j", "Imercfy@2025")
        )
    
    def close(self):
        self.driver.close()
    
    def get_company_info(self):
        """Get company information"""
        try:
            with self.driver.session() as session:
                result = session.run("""
                    MATCH (c:Company)
                    RETURN c.name as name, c.industry as industry, 
                           c.company_size as size, c.about as about
                """)
                return result.single()
        except Exception as e:
            print(f"Error getting company info: {e}")
            return None
    
    def find_jobs_by_query(self, query):
        """Find jobs based on user query - returns structured data for tables"""
        try:
            with self.driver.session() as session:
                # Get all jobs with complete information
                result = session.run("""
                    MATCH (j:Job)
                    OPTIONAL MATCH (j)-[:BELONGS_TO_DEPARTMENT]->(d:Department)
                    OPTIONAL MATCH (j)-[:REQUIRES_SKILL]->(s:Skill)
                    OPTIONAL MATCH (j)-[:AVAILABLE_AT]->(l:Location)
                    RETURN j.job_title as job_title,
                           j.job_id as job_id,
                           d.name as department,
                           j.experience_level as experience_level,
                           j.salary_range as salary_range,
                           j.workplace_type as workplace_type,
                           collect(DISTINCT s.name) as required_skills,
                           collect(DISTINCT l.name) as locations
                    ORDER BY j.job_title
                    LIMIT 10
                """)
                
                jobs = []
                for record in result:
                    jobs.append({
                        "job_title": record["job_title"],
                        "job_id": record["job_id"],
                        "department": record["department"] or "Not specified",
                        "experience_level": record["experience_level"] or {"minimum": 0, "preferred": 2},
                        "salary_range": record["salary_range"] or {"min": 0, "max": 0, "currency": "INR"},
                        "workplace_type": record["workplace_type"] or "Not specified",
                        "required_skills": record["required_skills"] or [],
                        "locations": record["locations"] or []
                    })
                
                # Return jobs array directly, not wrapped in another object
                return jobs  # ← Changed this line
        except Exception as e:
            print(f"Error finding jobs: {e}")
            return []  # ← Return empty array, not wrapped object
    
    def get_salary_info(self, query: str = "") -> Dict[str, Any]:
        """Get salary information for jobs"""
        try:
            with self.driver.session() as session:
                result = session.run("""
                    MATCH (j:Job)
                    OPTIONAL MATCH (j)-[:BELONGS_TO_DEPARTMENT]->(d:Department)
                    WHERE j.salary_range IS NOT NULL
                    RETURN j.job_title as job_title, 
                           j.salary_range as salary_range,
                           j.experience_level as experience_level,
                           d.name as department
                    ORDER BY j.job_title
                """)
                
                salary_data = []
                for record in result:
                    salary_data.append({
                        "job_title": record["job_title"],
                        "salary_range": record["salary_range"],
                        "experience_level": record["experience_level"] or "Not specified",
                        "department": record["department"] or "Not specified"
                    })
                
                return {"salary_ranges": salary_data}
        except Exception as e:
            print(f"Error getting salary info: {e}")
            return {"salary_ranges": []}
    
    def get_skills_analysis(self) -> Dict[str, Any]:
        """Get skills analysis with job counts"""
        try:
            with self.driver.session() as session:
                result = session.run("""
                    MATCH (j:Job)-[:REQUIRES_SKILL]->(s:Skill)
                    RETURN s.name as skill_name, 
                           count(j) as job_count,
                           s.category as category
                    ORDER BY job_count DESC
                    LIMIT 20
                """)
                
                skills = []
                for record in result:
                    skills.append({
                        "name": record["skill_name"],
                        "job_count": record["job_count"],
                        "category": record["category"] or "Technical"
                    })
                
                return {"skills": skills}
        except Exception as e:
            print(f"Error getting skills analysis: {e}")
            return {"skills": []}
    
    def get_department_info(self) -> Dict[str, Any]:
        """Get department information"""
        try:
            with self.driver.session() as session:
                result = session.run("""
                    MATCH (d:Department)<-[:BELONGS_TO_DEPARTMENT]-(j:Job)
                    RETURN d.name as department_name, 
                           count(j) as job_count,
                           collect(DISTINCT j.job_title) as positions
                    ORDER BY job_count DESC
                """)
                
                departments = []
                for record in result:
                    departments.append({
                        "name": record["department_name"],
                        "job_count": record["job_count"],
                        "positions": record["positions"] or []
                    })
                
                return {"departments": departments}
        except Exception as e:
            print(f"Error getting department info: {e}")
            return {"departments": []}
