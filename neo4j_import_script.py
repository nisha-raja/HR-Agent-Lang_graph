# neo4j_import_script.py
import json
from neo4j import GraphDatabase
import os

class TwilightJobsImporter:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
    
    def close(self):
        self.driver.close()
    
    def clear_database(self):
        """Clear all existing data"""
        with self.driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")
            print("✅ Database cleared")
    
    def create_constraints(self):
        """Create unique constraints"""
        with self.driver.session() as session:
            try:
                session.run("CREATE CONSTRAINT company_name IF NOT EXISTS FOR (c:Company) REQUIRE c.name IS UNIQUE")
                session.run("CREATE CONSTRAINT job_id IF NOT EXISTS FOR (j:Job) REQUIRE j.job_id IS UNIQUE")
                # Remove the skill constraint since skills can be shared across jobs
                session.run("CREATE CONSTRAINT location_name IF NOT EXISTS FOR (l:Location) REQUIRE l.name IS UNIQUE")
                session.run("CREATE CONSTRAINT department_name IF NOT EXISTS FOR (d:Department) REQUIRE d.name IS UNIQUE")
                print("✅ Constraints created")
            except Exception as e:
                print(f"⚠️ Some constraints may already exist: {e}")
    
    def import_company_data(self, company_info):
        """Import company information"""
        with self.driver.session() as session:
            # Create Company node
            session.run("""
                CREATE (c:Company {
                    name: $name,
                    industry: $industry,
                    company_size: $company_size,
                    about: $about
                })
            """, company_info)
            
            # Create Location nodes and relationships
            for location in company_info['locations']:
                session.run("""
                    MATCH (c:Company {name: $company_name})
                    MERGE (l:Location {
                        city: $city,
                        state: $state,
                        country: $country,
                        address: $address
                    })
                    MERGE (c)-[:HAS_OFFICE]->(l)
                """, {
                    'company_name': company_info['name'],
                    'city': location['city'],
                    'state': location['state'],
                    'country': location['country'],
                    'address': location['address']
                })
            
            # Create Technology nodes and relationships
            for category, techs in company_info['technologies'].items():
                for tech in techs:
                    session.run("""
                        MATCH (c:Company {name: $company_name})
                        MERGE (t:Technology {name: $tech_name, category: $category})
                        MERGE (c)-[:USES_TECHNOLOGY]->(t)
                    """, {
                        'company_name': company_info['name'],
                        'tech_name': tech,
                        'category': category
                    })
            
            # Create Industry nodes and relationships
            for industry in company_info['industries_served']:
                session.run("""
                    MATCH (c:Company {name: $company_name})
                    MERGE (i:Industry {name: $industry_name})
                    MERGE (c)-[:SERVES_INDUSTRY]->(i)
                """, {
                    'company_name': company_info['name'],
                    'industry_name': industry
                })
            
            print(f"✅ Company data imported: {company_info['name']}")
    
    def import_job_positions(self, job_positions):
        """Import job positions"""
        with self.driver.session() as session:
            for job in job_positions:
                try:
                    # Create Job node
                    session.run("""
                        CREATE (j:Job {
                            job_id: $job_id,
                            job_title: $job_title,
                            workplace_type: $workplace_type,
                            employment_type: $employment_type,
                            min_experience: $min_exp,
                            preferred_experience: $pref_exp,
                            min_salary: $min_salary,
                            max_salary: $max_salary,
                            currency: $currency,
                            role_category: $role_category,
                            industry_type: $industry_type
                        })
                    """, {
                        'job_id': job['job_id'],
                        'job_title': job['job_title'],
                        'workplace_type': job['workplace_type'],
                        'employment_type': job['employment_type'],
                        'min_exp': job['experience_level']['minimum'],
                        'pref_exp': job['experience_level']['preferred'],
                        'min_salary': job['salary_range']['min'],
                        'max_salary': job['salary_range']['max'],
                        'currency': job['salary_range']['currency'],
                        'role_category': job['role_category'],
                        'industry_type': job['industry_type']
                    })
                    
                    # Create Department node and relationship
                    session.run("""
                        MATCH (j:Job {job_id: $job_id})
                        MERGE (d:Department {name: $dept_name})
                        MERGE (j)-[:BELONGS_TO_DEPARTMENT]->(d)
                    """, {
                        'job_id': job['job_id'],
                        'dept_name': job['department']
                    })
                    
                    # Create Location relationships
                    for location in job['locations']:
                        session.run("""
                            MATCH (j:Job {job_id: $job_id})
                            MERGE (l:Location {name: $location_name})
                            MERGE (j)-[:AVAILABLE_AT]->(l)
                        """, {
                            'job_id': job['job_id'],
                            'location_name': location
                        })
                    
                    # Create Required Skills relationships (using MERGE for skills)
                    for skill in job['required_skills']:
                        session.run("""
                            MATCH (j:Job {job_id: $job_id})
                            MERGE (s:Skill {name: $skill_name})
                            ON CREATE SET s.type = 'required'
                            ON MATCH SET s.type = CASE 
                                WHEN s.type = 'preferred' THEN 'both'
                                ELSE s.type
                            END
                            MERGE (j)-[:REQUIRES_SKILL]->(s)
                        """, {
                            'job_id': job['job_id'],
                            'skill_name': skill
                        })
                    
                    # Create Preferred Skills relationships (using MERGE for skills)
                    for skill in job['preferred_skills']:
                        session.run("""
                            MATCH (j:Job {job_id: $job_id})
                            MERGE (s:Skill {name: $skill_name})
                            ON CREATE SET s.type = 'preferred'
                            ON MATCH SET s.type = CASE 
                                WHEN s.type = 'required' THEN 'both'
                                ELSE s.type
                            END
                            MERGE (j)-[:PREFERS_SKILL]->(s)
                        """, {
                            'job_id': job['job_id'],
                            'skill_name': skill
                        })
                    
                    # Create Responsibility nodes
                    for i, responsibility in enumerate(job['key_responsibilities']):
                        session.run("""
                            MATCH (j:Job {job_id: $job_id})
                            CREATE (r:Responsibility {
                                description: $description,
                                order: $order
                            })
                            MERGE (j)-[:HAS_RESPONSIBILITY]->(r)
                        """, {
                            'job_id': job['job_id'],
                            'description': responsibility,
                            'order': i + 1
                        })
                    
                    # Create Perk nodes
                    for perk in job['perks_benefits']:
                        session.run("""
                            MATCH (j:Job {job_id: $job_id})
                            MERGE (p:Perk {name: $perk_name})
                            MERGE (j)-[:OFFERS_PERK]->(p)
                        """, {
                            'job_id': job['job_id'],
                            'perk_name': perk
                        })
                    
                    # Link job to company
                    session.run("""
                        MATCH (j:Job {job_id: $job_id})
                        MATCH (c:Company {name: $company_name})
                        MERGE (c)-[:HAS_JOB]->(j)
                    """, {
                        'job_id': job['job_id'],
                        'company_name': 'Twilight IT Solutions Pvt Ltd'
                    })
                    
                    print(f"✅ Job imported: {job['job_title']}")
                    
                except Exception as e:
                    print(f"❌ Error importing job {job['job_id']}: {str(e)}")
                    continue
            
            print(f"✅ Job positions import completed")
    
    def import_data(self, json_file_path):
        """Main import function"""
        try:
            # Load JSON data
            with open(json_file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
            
            print("🚀 Starting Neo4j import...")
            
            # Clear existing data
            self.clear_database()
            
            # Create constraints
            self.create_constraints()
            
            # Import company data
            self.import_company_data(data['company_info'])
            
            # Import job positions
            self.import_job_positions(data['job_positions'])
            
            print("🎉 Import completed successfully!")
            
        except Exception as e:
            print(f"❌ Error during import: {str(e)}")

def main():
    # Neo4j connection details
    URI = "neo4j://127.0.0.1:7687"
    USER = "neo4j"
    PASSWORD = "Imercfy@2025"
    
    # Create importer instance
    importer = TwilightJobsImporter(URI, USER, PASSWORD)
    
    try:
        # Import data
        importer.import_data("twi_jobs_dataset.json")
        
        # Test queries
        print("\n Testing queries...")
        with importer.driver.session() as session:
            # Count nodes
            result = session.run("MATCH (n) RETURN labels(n) as labels, count(n) as count")
            print("\n📊 Node counts:")
            for record in result:
                print(f"  {record['labels']}: {record['count']}")
            
            # Count relationships
            result = session.run("MATCH ()-[r]->() RETURN type(r) as type, count(r) as count")
            print("\n🔗 Relationship counts:")
            for record in result:
                print(f"  {record['type']}: {record['count']}")
            
            # Show some sample data
            print("\n📋 Sample Jobs:")
            result = session.run("MATCH (j:Job) RETURN j.job_title as title, j.job_id as id LIMIT 5")
            for record in result:
                print(f"  {record['id']}: {record['title']}")
                
    finally:
        importer.close()

if __name__ == "__main__":
    main()
