"""
seed.py
---------
Seeds the database with realistic demonstration data: users (Admin,
Engineer, Viewer), a sample BHEL power-plant project with full hierarchy
(Units -> Areas -> Systems -> Equipment), vendors, equipment categories and
sample progress logs.

Usage:
    python seed.py
"""

import random
from datetime import date, timedelta, datetime

from app import create_app
from app.extensions import db
from app.models import (
    User, Role, Project, ProjectStatus, Unit, Area, System,
    EquipmentCategory, Equipment, EquipmentStatus, Vendor,
    DailyProgress, WeeklyProgress, MonthlyProgress,
)

app = create_app("development")


def seed():
    with app.app_context():
        print("Dropping & recreating all tables ...")
        db.drop_all()
        db.create_all()

        # ------------------------------------------------------------------
        # Users
        # ------------------------------------------------------------------
        print("Creating users ...")
        admin = User(
            employee_code="BHEL0001", full_name="Rajesh Kumar", email="admin@bhel.in",
            username="admin", role=Role.ADMIN, department="IT & Systems", designation="Deputy General Manager",
            phone="9876500001",
        )
        admin.set_password("Admin@123")

        engineer1 = User(
            employee_code="BHEL0002", full_name="Anita Sharma", email="anita.sharma@bhel.in",
            username="engineer1", role=Role.ENGINEER, department="Site Execution", designation="Senior Engineer",
            phone="9876500002",
        )
        engineer1.set_password("Engineer@123")

        engineer2 = User(
            employee_code="BHEL0003", full_name="Vikram Singh", email="vikram.singh@bhel.in",
            username="engineer2", role=Role.ENGINEER, department="Site Execution", designation="Engineer",
            phone="9876500003",
        )
        engineer2.set_password("Engineer@123")

        viewer = User(
            employee_code="BHEL0004", full_name="Suresh Reddy", email="suresh.reddy@bhel.in",
            username="viewer", role=Role.VIEWER, department="Client Coordination", designation="Manager",
            phone="9876500004",
        )
        viewer.set_password("Viewer@123")

        db.session.add_all([admin, engineer1, engineer2, viewer])
        db.session.commit()

        # ------------------------------------------------------------------
        # Vendors
        # ------------------------------------------------------------------
        print("Creating vendors ...")
        vendors_data = [
            ("Kirloskar Brothers Ltd", "VEN-0001", "Pumps & Valves", 4.2),
            ("Larsen & Toubro Electrical", "VEN-0002", "Electrical & Switchgear", 4.5),
            ("Thermax Ltd", "VEN-0003", "Boilers & Heat Exchangers", 4.0),
            ("ABB India Ltd", "VEN-0004", "Instrumentation & Controls", 4.6),
            ("Siemens Ltd India", "VEN-0005", "Turbines & Generators", 4.7),
            ("Schneider Electric India", "VEN-0006", "Automation Systems", 4.3),
        ]
        vendors = []
        for name, code, spec, rating in vendors_data:
            v = Vendor(
                name=name, vendor_code=code, specialization=spec, rating=rating,
                contact_person="Vendor Contact", email=f"contact@{code.lower()}.example.com",
                phone="9800000000", is_active=True,
            )
            vendors.append(v)
        db.session.add_all(vendors)
        db.session.commit()

        # ------------------------------------------------------------------
        # Equipment Categories
        # ------------------------------------------------------------------
        print("Creating equipment categories ...")
        categories_data = [
            ("Pump", "CAT-PUMP"), ("Valve", "CAT-VALVE"), ("Motor", "CAT-MOTOR"),
            ("Transformer", "CAT-TXFR"), ("Boiler", "CAT-BOILER"), ("Turbine", "CAT-TURB"),
            ("Switchgear", "CAT-SWGR"), ("Instrument", "CAT-INST"),
        ]
        categories = [EquipmentCategory(name=n, code=c) for n, c in categories_data]
        db.session.add_all(categories)
        db.session.commit()

        # ------------------------------------------------------------------
        # Project hierarchy
        # ------------------------------------------------------------------
        print("Creating project hierarchy ...")
        project = Project(
            project_code="NTPC-DRLP-800",
            name="NTPC Darlipali Super Thermal Power Project",
            client_name="NTPC Limited",
            location="Darlipali, Odisha",
            capacity_mw=1600,
            contract_value_crore=3250.5,
            start_date=date(2023, 4, 1),
            scheduled_end_date=date(2027, 3, 31),
            status=ProjectStatus.IN_PROGRESS,
            project_manager="Rajesh Kumar",
            description="EPC execution of 2x800MW supercritical thermal power units including "
                        "BTG (Boiler, Turbine, Generator) package for NTPC Limited.",
        )
        project2 = Project(
            project_code="NPCIL-KKNPP-3&4",
            name="Kudankulam Nuclear Power Project Units 3 & 4",
            client_name="NPCIL",
            location="Kudankulam, Tamil Nadu",
            capacity_mw=2000,
            contract_value_crore=5100.0,
            start_date=date(2022, 1, 15),
            scheduled_end_date=date(2026, 12, 31),
            status=ProjectStatus.DELAYED,
            project_manager="Vikram Singh",
            description="Balance of Plant electro-mechanical works for Units 3 & 4.",
        )
        db.session.add_all([project, project2])
        db.session.commit()

        area_names = [
            ("Boiler Area", "BLR"), ("Turbine Generator Area", "TG"),
            ("Coal Handling Plant", "CHP"), ("Ash Handling Plant", "AHP"),
            ("Water Treatment Plant", "WTP"), ("Electrical Switchyard", "ESY"),
        ]
        system_names = [
            ("Feed Water System", "FWS"), ("Cooling Water System", "CWS"),
            ("Compressed Air System", "CAS"), ("Fuel Oil System", "FOS"),
            ("Flue Gas Desulphurization", "FGD"), ("Condensate Extraction System", "CES"),
        ]
        equipment_names = [
            "Boiler Feed Pump", "Circulating Water Pump", "Isolation Valve", "Control Valve",
            "Induced Draft Fan Motor", "Forced Draft Fan Motor", "Main Power Transformer",
            "Auxiliary Transformer", "Steam Turbine", "Generator", "HT Switchgear Panel",
            "Flow Transmitter", "Pressure Transmitter", "Temperature Sensor",
        ]

        engineers = [engineer1, engineer2]
        equipment_counter = 1

        for proj in (project, project2):
            for u_idx in range(1, 3):  # 2 units per project
                unit = Unit(
                    project_id=proj.id, name=f"Unit-{u_idx} ({int(proj.capacity_mw/2)}MW)",
                    unit_code=f"U{u_idx}", capacity_mw=proj.capacity_mw / 2,
                )
                db.session.add(unit)
                db.session.commit()

                for a_name, a_code in random.sample(area_names, 3):
                    area = Area(
                        unit_id=unit.id, name=a_name, area_code=f"{a_code}-{u_idx}",
                        description=f"{a_name} for {unit.name}",
                    )
                    db.session.add(area)
                    db.session.commit()

                    for s_name, s_code in random.sample(system_names, 2):
                        system = System(
                            area_id=area.id, name=s_name, system_code=f"{s_code}-{u_idx}-{area.id}",
                            description=f"{s_name} within {a_name}",
                        )
                        db.session.add(system)
                        db.session.commit()

                        for eq_name in random.sample(equipment_names, 3):
                            install_pct = round(random.uniform(20, 100), 1)
                            commission_pct = round(random.uniform(0, install_pct), 1)
                            status = random.choice(EquipmentStatus.ALL)
                            expected = date.today() + timedelta(days=random.randint(-20, 60))
                            equipment = Equipment(
                                system_id=system.id,
                                category_id=random.choice(categories).id,
                                vendor_id=random.choice(vendors).id,
                                assigned_engineer_id=random.choice(engineers).id,
                                equipment_name=eq_name,
                                equipment_code=f"EQ-{equipment_counter:05d}",
                                drawing_number=f"DWG-{equipment_counter:04d}-R0",
                                po_number=f"PO-2024-{equipment_counter:04d}",
                                status=status,
                                installation_progress=install_pct,
                                commissioning_progress=commission_pct,
                                remarks="Progressing as per schedule." if install_pct > 50 else "Awaiting material clearance.",
                                expected_date=expected,
                                actual_date=expected if status == EquipmentStatus.COMMISSIONED else None,
                            )
                            db.session.add(equipment)
                            equipment_counter += 1
                        db.session.commit()
                        system.recalculate_progress()
                    db.session.commit()
                    area.recalculate_progress()
                db.session.commit()
                unit.recalculate_progress()
            db.session.commit()
            proj.recalculate_progress()
        db.session.commit()

        # ------------------------------------------------------------------
        # Sample progress logs
        # ------------------------------------------------------------------
        print("Creating sample progress logs ...")
        sample_equipment = Equipment.query.limit(10).all()
        for eq in sample_equipment:
            for days_ago in (1, 2, 3):
                db.session.add(DailyProgress(
                    equipment_id=eq.id, logged_by_id=eq.assigned_engineer_id,
                    log_date=date.today() - timedelta(days=days_ago),
                    installation_progress=max(0, eq.installation_progress - days_ago * 2),
                    commissioning_progress=max(0, eq.commissioning_progress - days_ago),
                    activity_description="Routine installation and inspection activity carried out.",
                    manpower_deployed=random.randint(4, 15),
                ))
            db.session.add(WeeklyProgress(
                equipment_id=eq.id, logged_by_id=eq.assigned_engineer_id,
                week_start_date=date.today() - timedelta(days=7), week_end_date=date.today(),
                planned_progress=min(100, eq.installation_progress + 5),
                actual_progress=eq.installation_progress,
                summary="Weekly progress summary recorded.",
            ))
            db.session.add(MonthlyProgress(
                equipment_id=eq.id, logged_by_id=eq.assigned_engineer_id,
                month=date.today().month, year=date.today().year,
                planned_progress=min(100, eq.installation_progress + 10),
                actual_progress=eq.installation_progress,
                summary="Monthly progress summary recorded.",
            ))
        db.session.commit()

        print("Seed data created successfully.")
        print("-" * 60)
        print("Login credentials:")
        print("  Admin    -> username: admin     password: Admin@123")
        print("  Engineer -> username: engineer1  password: Engineer@123")
        print("  Viewer   -> username: viewer     password: Viewer@123")
        print("-" * 60)


if __name__ == "__main__":
    seed()
