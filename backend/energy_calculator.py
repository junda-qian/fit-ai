"""
Energy Intake Calculator Module

Calculates various energy expenditure metrics based on user's physical attributes
and training schedule.
"""

from pydantic import BaseModel, Field
from typing import Optional


class EnergyCalculatorInput(BaseModel):
    """Input parameters for energy calculation"""
    bodyweight_kg: float = Field(..., gt=0, description="Bodyweight in kilograms")
    body_fat_percentage: float = Field(..., ge=0, le=100, description="Body fat percentage (0-100)")
    physical_activity_factor: float = Field(..., ge=1.0, le=1.5, description="Physical Activity Factor (1.0-1.5)")
    thermic_effect_food_factor: float = Field(..., ge=1.0, le=1.25, description="Thermic Effect of Food factor (1.0-1.25)")
    training_duration_min: float = Field(..., gt=0, description="Duration of weight training session in minutes")
    energy_balance_factor: float = Field(..., gt=0, description="Energy balance factor (e.g., 1.05 for 5% surplus, 0.8 for 20% deficit)")
    training_days_per_week: int = Field(..., ge=0, le=7, description="Number of training days per week")


class MacroTargets(BaseModel):
    """Macro nutrient targets"""
    protein_grams: float
    protein_calories: float
    fat_grams: float
    fat_calories: float
    carbs_grams: float
    carbs_calories: float
    protein_percentage: float
    fat_percentage: float
    carbs_percentage: float


class EnergyCalculatorOutput(BaseModel):
    """Output results from energy calculation"""
    fat_free_mass_kg: float
    cunningham_bmr: float
    training_energy_expenditure: float
    rest_day_energy_expenditure: float
    training_day_energy_expenditure: float
    maintenance_energy_intake: float
    average_target_energy_intake: float
    macro_targets: MacroTargets


class EnergyCalculator:
    """Calculator for energy expenditure and intake metrics"""

    @staticmethod
    def calculate_fat_free_mass(bodyweight_kg: float, body_fat_percentage: float) -> float:
        """
        Calculate fat-free mass

        Formula: Bodyweight (kg) * (1 - Body fat percentage (%) / 100)
        """
        return bodyweight_kg * (1 - body_fat_percentage / 100)

    @staticmethod
    def calculate_cunningham_bmr(fat_free_mass_kg: float) -> float:
        """
        Calculate Basal Metabolic Rate using Cunningham et al. (1991) formula

        Formula: 370 + (21.6 * Fat-free mass (kg))
        """
        return 370 + (21.6 * fat_free_mass_kg)

    @staticmethod
    def calculate_training_energy_expenditure(bodyweight_kg: float, training_duration_min: float) -> float:
        """
        Calculate energy expenditure during training

        Formula: 0.1 * Bodyweight (kg) * Duration of weight training session (min)
        """
        return 0.1 * bodyweight_kg * training_duration_min

    @staticmethod
    def calculate_rest_day_expenditure(
        cunningham_bmr: float,
        physical_activity_factor: float,
        thermic_effect_food_factor: float
    ) -> float:
        """
        Calculate rest day energy expenditure

        Formula: Cunningham BMR * Physical Activity Factor * Thermic Effect of Food factor
        """
        return cunningham_bmr * physical_activity_factor * thermic_effect_food_factor

    @staticmethod
    def calculate_training_day_expenditure(
        cunningham_bmr: float,
        physical_activity_factor: float,
        training_energy_expenditure: float,
        thermic_effect_food_factor: float
    ) -> float:
        """
        Calculate training day energy expenditure

        Formula: (Cunningham BMR * Physical Activity Factor + Training EE) * Thermic Effect of Food factor
        """
        return (cunningham_bmr * physical_activity_factor + training_energy_expenditure) * thermic_effect_food_factor

    @staticmethod
    def calculate_maintenance_energy_intake(
        training_days_per_week: int,
        training_day_expenditure: float,
        rest_day_expenditure: float
    ) -> float:
        """
        Calculate maintenance energy intake (weekly average)

        Formula: (Training days * Training day EE + Rest days * Rest day EE) / 7
        """
        rest_days_per_week = 7 - training_days_per_week
        return (
            training_days_per_week * training_day_expenditure +
            rest_days_per_week * rest_day_expenditure
        ) / 7

    @staticmethod
    def calculate_target_energy_intake(
        maintenance_energy_intake: float,
        energy_balance_factor: float
    ) -> float:
        """
        Calculate average target energy intake

        Formula: Maintenance energy intake * Energy balance factor
        """
        return maintenance_energy_intake * energy_balance_factor

    @staticmethod
    def calculate_macro_targets(bodyweight_kg: float, target_energy_intake: float) -> MacroTargets:
        """
        Calculate macro nutrient targets based on target energy intake

        Macro calculation order:
        1. Protein: 1.6g per kg bodyweight
        2. Protein calories: protein_grams * 4
        3. Fat calories: target_energy_intake * 0.3
        4. Fat grams: fat_calories / 9
        5. Carbs calories: remaining calories after protein and fat
        6. Carbs grams: carbs_calories / 4

        Args:
            bodyweight_kg: Bodyweight in kilograms
            target_energy_intake: Target daily energy intake in calories

        Returns:
            MacroTargets object with all macro calculations
        """
        # Constants
        PROTEIN_KCAL_PER_GRAM = 4
        FAT_KCAL_PER_GRAM = 9
        CARBS_KCAL_PER_GRAM = 4
        PROTEIN_PER_KG = 1.6
        FAT_PERCENTAGE = 0.3

        # 1. Calculate protein in grams
        protein_grams = bodyweight_kg * PROTEIN_PER_KG

        # 2. Calculate protein in calories
        protein_calories = protein_grams * PROTEIN_KCAL_PER_GRAM

        # 3. Calculate fat in calories (30% of target energy intake)
        fat_calories = target_energy_intake * FAT_PERCENTAGE

        # 4. Calculate fat in grams
        fat_grams = fat_calories / FAT_KCAL_PER_GRAM

        # 5. Calculate remaining calories for carbs
        carbs_calories = target_energy_intake - protein_calories - fat_calories

        # 6. Calculate carbs in grams
        carbs_grams = carbs_calories / CARBS_KCAL_PER_GRAM

        # Calculate percentages
        protein_percentage = (protein_calories / target_energy_intake) * 100
        fat_percentage = (fat_calories / target_energy_intake) * 100
        carbs_percentage = (carbs_calories / target_energy_intake) * 100

        return MacroTargets(
            protein_grams=round(protein_grams, 1),
            protein_calories=round(protein_calories, 1),
            fat_grams=round(fat_grams, 1),
            fat_calories=round(fat_calories, 1),
            carbs_grams=round(carbs_grams, 1),
            carbs_calories=round(carbs_calories, 1),
            protein_percentage=round(protein_percentage, 1),
            fat_percentage=round(fat_percentage, 1),
            carbs_percentage=round(carbs_percentage, 1)
        )

    @classmethod
    def calculate_all(cls, input_data: EnergyCalculatorInput) -> EnergyCalculatorOutput:
        """
        Calculate all energy metrics from input parameters

        Args:
            input_data: EnergyCalculatorInput object with all required parameters

        Returns:
            EnergyCalculatorOutput object with all calculated metrics
        """
        # Step 1: Calculate fat-free mass
        fat_free_mass = cls.calculate_fat_free_mass(
            input_data.bodyweight_kg,
            input_data.body_fat_percentage
        )

        # Step 2: Calculate Cunningham BMR
        cunningham_bmr = cls.calculate_cunningham_bmr(fat_free_mass)

        # Step 3: Calculate training energy expenditure
        training_ee = cls.calculate_training_energy_expenditure(
            input_data.bodyweight_kg,
            input_data.training_duration_min
        )

        # Step 4: Calculate rest day energy expenditure
        rest_day_ee = cls.calculate_rest_day_expenditure(
            cunningham_bmr,
            input_data.physical_activity_factor,
            input_data.thermic_effect_food_factor
        )

        # Step 5: Calculate training day energy expenditure
        training_day_ee = cls.calculate_training_day_expenditure(
            cunningham_bmr,
            input_data.physical_activity_factor,
            training_ee,
            input_data.thermic_effect_food_factor
        )

        # Step 6: Calculate maintenance energy intake
        maintenance_ei = cls.calculate_maintenance_energy_intake(
            input_data.training_days_per_week,
            training_day_ee,
            rest_day_ee
        )

        # Step 7: Calculate target energy intake
        target_ei = cls.calculate_target_energy_intake(
            maintenance_ei,
            input_data.energy_balance_factor
        )

        # Step 8: Calculate macro targets
        macro_targets = cls.calculate_macro_targets(
            input_data.bodyweight_kg,
            target_ei
        )

        return EnergyCalculatorOutput(
            fat_free_mass_kg=round(fat_free_mass, 2),
            cunningham_bmr=round(cunningham_bmr, 2),
            training_energy_expenditure=round(training_ee, 2),
            rest_day_energy_expenditure=round(rest_day_ee, 2),
            training_day_energy_expenditure=round(training_day_ee, 2),
            maintenance_energy_intake=round(maintenance_ei, 2),
            average_target_energy_intake=round(target_ei, 2),
            macro_targets=macro_targets
        )
