import csv
from django.core.management.base import BaseCommand
from core.models import SoilData  # Update with your app name

class Command(BaseCommand):
    help = "Import soil data from CSV"

    def handle(self, *args, **kwargs):
        file_path = 'soil_data.csv'  # Make sure this is in the same directory as manage.py
        try:
            with open(file_path, 'r') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    SoilData.objects.create(
                        nitrogen=float(row['Nitrogen']),
                        phosphorus=float(row['Phosphorus']),
                        potassium=float(row['Potassium']),
                        ph=float(row['pH']),
                        rainfall=float(row['Rainfall']),
                        temperature=float(row['Temperature']),
                        recommended_crop=row['Recommended Crop']
                    )
            self.stdout.write(self.style.SUCCESS("✅ Soil data imported successfully!"))
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR("❌ CSV file not found. Please check the file path."))
