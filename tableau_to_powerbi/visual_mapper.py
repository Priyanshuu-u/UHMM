import logging
from enum import Enum
import json

logger = logging.getLogger(__name__)

class TableauVisualType(Enum):
    BAR = "bar"
    LINE = "line"
    PIE = "pie"
    SCATTER = "scatter"
    MAP = "map"
    TEXT = "text"
    TABLE = "table"
    TREEMAP = "treemap"
    AREA = "area"
    GANTT = "gantt"
    BOXPLOT = "boxplot"
    HEATMAP = "heatmap"
    BUBBLE = "bubble"
    AUTOMATIC = "automatic"

class PowerBIVisualType(Enum):
    COLUMN_CHART = "columnChart"
    LINE_CHART = "lineChart"
    PIE_CHART = "pieChart"
    SCATTER_CHART = "scatterChart"
    MAP = "map"
    CARD = "card"
    TABLE = "table"
    TREEMAP = "treemap"
    AREA_CHART = "areaChart"
    GANTT = "gantt"
    BOX_WHISKER_CHART = "boxWhiskerChart"
    HEAT_MAP = "heatMap"
    BUBBLE_CHART = "bubbleChart"

class VisualMapper:
    """
    Maps Tableau visualizations to their Power BI equivalents using AI-driven recognition
    """
    
    def __init__(self):
        # Visual type mapping from Tableau to Power BI
        self.type_mapping = {
            TableauVisualType.BAR.value: PowerBIVisualType.COLUMN_CHART.value,
            TableauVisualType.LINE.value: PowerBIVisualType.LINE_CHART.value,
            TableauVisualType.PIE.value: PowerBIVisualType.PIE_CHART.value,
            TableauVisualType.SCATTER.value: PowerBIVisualType.SCATTER_CHART.value,
            TableauVisualType.MAP.value: PowerBIVisualType.MAP.value,
            TableauVisualType.TEXT.value: PowerBIVisualType.CARD.value,
            TableauVisualType.TABLE.value: PowerBIVisualType.TABLE.value,
            TableauVisualType.TREEMAP.value: PowerBIVisualType.TREEMAP.value,
            TableauVisualType.AREA.value: PowerBIVisualType.AREA_CHART.value,
            TableauVisualType.GANTT.value: PowerBIVisualType.GANTT.value,
            TableauVisualType.BOXPLOT.value: PowerBIVisualType.BOX_WHISKER_CHART.value,
            TableauVisualType.HEATMAP.value: PowerBIVisualType.HEAT_MAP.value,
            TableauVisualType.BUBBLE.value: PowerBIVisualType.BUBBLE_CHART.value,
            TableauVisualType.AUTOMATIC.value: PowerBIVisualType.COLUMN_CHART.value  # Default fallback
        }
        
        # Load the AI model for advanced visualization recognition
        self.ai_model = self._load_ai_model()
    
    def map_visuals(self, worksheets):
        """
        Map Tableau visualizations to Power BI equivalents
        
        Args:
            worksheets: List of worksheets with visualization information
            
        Returns:
            List of Power BI visual configurations
        """
        logger.info("Mapping Tableau visualizations to Power BI")
        
        power_bi_visuals = []
        
        for worksheet in worksheets:
            for viz in worksheet['visualizations']:
                # Get basic mapping by type
                tableau_type = viz['type']
                power_bi_type = self.type_mapping.get(
                    tableau_type, 
                    PowerBIVisualType.COLUMN_CHART.value  # Default fallback
                )
                
                # Use AI to improve mapping accuracy by analyzing the visualization structure
                if self.ai_model:
                    power_bi_type = self._enhance_mapping_with_ai(
                        tableau_type, 
                        viz['marks'], 
                        viz['encodings']
                    )
                
                # Create Power BI visual configuration
                visual_config = self._create_visual_config(
                    worksheet['name'],
                    power_bi_type,
                    viz['marks'],
                    viz['encodings'],
                    worksheet['fields'],
                    worksheet['filters']
                )
                
                power_bi_visuals.append(visual_config)
        
        return power_bi_visuals
    
    def _load_ai_model(self):
        """
        Load the AI model for enhanced visualization mapping
        In a real implementation, this would load a trained ML model
        """
        # Placeholder for actual AI model loading
        # In a real implementation, this might be:
        # return tensorflow.keras.models.load_model('visual_recognition_model.h5')
        
        # For now, return a simple rule-based system
        return {
            "rules": [
                {
                    "if": {"tableau_type": "bar", "has_dimension": True, "has_measure": True},
                    "then": "columnChart"
                },
                {
                    "if": {"tableau_type": "line", "has_date": True},
                    "then": "lineChart"
                },
                {
                    "if": {"tableau_type": "automatic", "has_lat_long": True},
                    "then": "map"
                }
                # More rules would be defined here
            ]
        }
    
    def _enhance_mapping_with_ai(self, tableau_type, marks, encodings):
        """
        Use AI to enhance the mapping accuracy
        
        Args:
            tableau_type: The Tableau visualization type
            marks: The mark properties
            encodings: The visual encodings
            
        Returns:
            The recommended Power BI visual type
        """
        # This is a simplified version - in a real implementation,
        # we would use machine learning to analyze the visualization structure
        
        # Check for rule matches in our simple rule-based system
        rules = self.ai_model.get("rules", [])
        
        # Extract features for rule matching
        has_dimension = any('dimension' in field.lower() for field in marks.values())
        has_measure = any('measure' in field.lower() for field in marks.values())
        has_date = any('date' in field.lower() for field in marks.values())
        has_lat_long = any('latitude' in field.lower() for field in marks.values()) and \
                      any('longitude' in field.lower() for field in marks.values())
        
        # Apply rules
        for rule in rules:
            conditions = rule["if"]
            matches = True
            
            # Check all conditions in the rule
            if conditions.get("tableau_type") and conditions["tableau_type"] != tableau_type:
                matches = False
            if conditions.get("has_dimension") and conditions["has_dimension"] != has_dimension:
                matches = False
            if conditions.get("has_measure") and conditions["has_measure"] != has_measure:
                matches = False
            if conditions.get("has_date") and conditions["has_date"] != has_date:
                matches = False
            if conditions.get("has_lat_long") and conditions["has_lat_long"] != has_lat_long:
                matches = False
            
            # If all conditions match, return the recommended visual type
            if matches:
                return rule["then"]
        
        # If no rules match, fall back to the basic mapping
        return self.type_mapping.get(tableau_type, PowerBIVisualType.COLUMN_CHART.value)
    
    def _create_visual_config(self, name, visual_type, marks, encodings, fields, filters):
        """
        Create a Power BI visual configuration
        
        Args:
            name: The name of the worksheet
            visual_type: The Power BI visual type
            marks: The mark properties
            encodings: The visual encodings
            fields: The fields used in the worksheet
            filters: The filters applied to the worksheet
            
        Returns:
            A dictionary with the Power BI visual configuration
        """
        # Map fields from Tableau to Power BI visual roles
        field_mappings = self._map_fields_to_roles(visual_type, marks, encodings, fields)
        
        # Map filters from Tableau to Power BI
        filter_mappings = self._map_filters(filters)
        
        # Create a unique visual name
        visual_name = f"{name}_visual_{visual_type}"
        
        # Basic visual configuration
        visual_config = {
            "name": visual_name,
            "type": visual_type,
            "fields": field_mappings,
            "filters": filter_mappings,
            "properties": self._get_default_properties(visual_type)
        }
        
        return visual_config
    
    def _map_fields_to_roles(self, visual_type, marks, encodings, fields):
        """Map Tableau fields to Power BI visual roles"""
        field_mappings = {}
        
        # Different visuals have different field roles
        if visual_type == PowerBIVisualType.COLUMN_CHART.value:
            # Map axis fields
            for key, value in marks.items():
                if key == "columns":
                    field_mappings["category"] = value
                elif key == "rows":
                    field_mappings["value"] = value
            
            # Map color, size, etc.
            for key, value in encodings.items():
                if key == "color":
                    field_mappings["series"] = value
                elif key == "size":
                    field_mappings["size"] = value
        
        elif visual_type == PowerBIVisualType.PIE_CHART.value:
            # Map category and values for pie chart
            for key, value in marks.items():
                if key == "columns" or key == "color":
                    field_mappings["legend"] = value
                elif key == "rows" or key == "size":
                    field_mappings["values"] = value
        
        # Add more visual type mappings as needed
        
        return field_mappings
    
    def _map_filters(self, filters):
        """Map Tableau filters to Power BI filters"""
        filter_mappings = []
        
        for filter_item in filters:
            filter_mappings.append({
                "field": filter_item["field"],
                "type": self._map_filter_type(filter_item["type"]),
                "values": filter_item["values"]
            })
        
        return filter_mappings
    
    def _map_filter_type(self, tableau_filter_type):
        """Map Tableau filter type to Power BI filter type"""
        # Simplified mapping
        mapping = {
            "categorical": "In",
            "quantitative": "Between",
            "relative_date": "RelativeDate",
            "boolean": "In"
        }
        
        return mapping.get(tableau_filter_type, "In")
    
    def _get_default_properties(self, visual_type):
        """Get default properties for a Power BI visual type"""
        # Default properties for various visual types
        properties = {
            "general": {
                "title": True,
                "legend": True
            }
        }
        
        # Add specific properties based on visual type
        if visual_type == PowerBIVisualType.COLUMN_CHART.value:
            properties["columnChart"] = {
                "showAxisTitles": True,
                "showDataLabels": False
            }
        elif visual_type == PowerBIVisualType.PIE_CHART.value:
            properties["pieChart"] = {
                "showDataLabels": True,
                "showPercentage": True
            }
        
        # Add more visual-specific properties as needed
        
        return properties