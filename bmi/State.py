def UpdateBmiState(bmi):
    result =""
    if bmi < 18.5:
        result = "IsThin: "
    if 18.5 <= bmi < 24:
        result = "IsNormal: "
    if 24<= bmi < 27:
        result = "Heavy: "
    if 27 <= bmi < 30:
         result = "Mild: "
    if 30<= bmi < 35:
         result = "Moderate: "
    if bmi >=35:
         result = "Severe: "
    return result
