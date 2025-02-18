from typing import Dict, List

def extract_relevant_items(suggestions: Dict, experiences: List[str], projects: List[str]) -> Dict[str, List[str]]:
    """
    Extract experience and project names from suggestions
    Returns dict with 'experiences' and 'projects' lists
    """
    relevant_items = {
        "experiences": [],
        "projects": []
    }
    
    for suggestion_type, suggestions_list in suggestions.items():
        # Skip if not a list of suggestions
        if not isinstance(suggestions_list, list):
            continue
            
        for suggestion in suggestions_list:
            # Extract the name from the suggestion
            if "Old text:" in suggestion:
                # Get text between "Old text:" and "New text:"
                old_text = suggestion.split("Old text:")[1].split("New text:")[0].strip()
                
                # Add to appropriate list based on suggestion type
                if suggestion_type.lower() == "experience suggestions":
                    relevant_items["experiences"].append(old_text)
                elif suggestion_type.lower() == "project suggestions":
                    relevant_items["projects"].append(old_text)

    return relevant_items