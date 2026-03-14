def generate_answer(objects, question):
    """Generate conversational answers about detected objects"""
    question_lower = question.lower()

    if not objects:
        return "I couldn't detect any objects in this image. Could you try uploading another image?"

    # Group objects by name for easier querying
    objects_by_name = {}
    for obj in objects:
        name = obj["name"]
        if name not in objects_by_name:
            objects_by_name[name] = []
        objects_by_name[name].append(obj)

    # Question about "what is" or "what objects"
    if "what is in" in question_lower or "what's in" in question_lower or "what objects" in question_lower:
        return list_detected_objects(objects)

    # Question about specific object - what is it
    if "what is" in question_lower or "what's" in question_lower:
        for obj in objects:
            if obj["name"].lower() in question_lower:
                return f"It's a {obj['name']}."
        # If not found in question, describe first object
        return f"It's a {objects[0]['name']}."

    # Question about colors
    if "color" in question_lower or "what color" in question_lower:
        for obj in objects:
            if obj["name"].lower() in question_lower:
                return f"The {obj['name']} is {obj['color']}."
        
        # List all colors
        color_desc = ", ".join([f"{obj['name']} is {obj['color']}" for obj in objects])
        return f"Here are the colors I see: {color_desc}."

    # Question about how many objects
    if "how many" in question_lower:
        for name in objects_by_name:
            if name in question_lower:
                count = len(objects_by_name[name])
                return f"I can see {count} {name}(s)."
        
        total = len(objects)
        return f"I can see {total} object(s)."

    # Question about position/location
    if "where" in question_lower or "position" in question_lower or "located" in question_lower:
        for obj in objects:
            if obj["name"].lower() in question_lower:
                return f"The {obj['name']} is at the {obj['position']}."
        
        positions = [f"{obj['name']} at {obj['position']}" for obj in objects]
        return f"Object positions: {', '.join(positions)}."

    # Question about specific object presence
    if "is there" in question_lower or "is it" in question_lower or "can you see" in question_lower:
        for name in objects_by_name:
            if name in question_lower:
                return f"Yes, I can see {len(objects_by_name[name])} {name}(s)."
        return "I couldn't find that specific object in the image."

    # Question about state/activity
    if "moving" in question_lower or "walking" in question_lower or "running" in question_lower or "state" in question_lower or "status" in question_lower or "doing" in question_lower:
        for obj in objects:
            if obj["name"].lower() in question_lower:
                return f"The {obj['name']} is {obj['state']}."
        return list_detected_objects(objects)

    # Question about confidence/accuracy
    if "confidence" in question_lower or "accuracy" in question_lower or "sure" in question_lower:
        for obj in objects:
            if obj["name"].lower() in question_lower:
                return f"I'm {obj['confidence'] * 100:.0f}% confident it's a {obj['name']}."
        
        confs = ', '.join([f"{obj['name']} ({obj['confidence'] * 100:.0f}%)" for obj in objects])
        return f"Detection confidence: {confs}."

    # Default response - just list objects
    return list_detected_objects(objects)


def list_detected_objects(objects):
    """Generate a simple list of detected objects"""
    if not objects:
        return "I couldn't detect any objects in this image."
    
    object_names = [obj['name'].capitalize() for obj in objects]
    
    if len(object_names) == 1:
        return f"I can see a {object_names[0]}."
    else:
        # Create a proper English list
        if len(object_names) == 2:
            return f"I can see a {object_names[0]} and a {object_names[1]}."
        else:
            return f"I can see {', '.join([f'a {name}' for name in object_names[:-1]])}, and a {object_names[-1]}."


def describe_single_object(obj):
    """Generate a detailed description of a single object"""
    return (
        f"This is a {obj['name']}. "
        f"It has a {obj['color']} color and is located at the {obj['position']} of the image. "
        f"The object appears to be {obj['state']}. "
        f"Detection confidence: {obj['confidence'] * 100:.0f}%."
    )