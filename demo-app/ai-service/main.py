from fastapi import FastAPI
import random

app = FastAPI()

@app.get("/")
def root():
    return {"message": "AI Infrastructure Optimizer Running"}

@app.get("/forecast")
def forecast():
    predicted_cpu = random.randint(30, 90)

    return {
        "predicted_cpu_usage": predicted_cpu,
        "recommended_action":
            "scale_up" if predicted_cpu > 70 else "scale_down"
    }

@app.get("/cost-estimate")
def cost():

    aws_cost = 0.24
    azure_cost = 0.21

    return {
        "aws_hourly_cost": aws_cost,
        "azure_hourly_cost": azure_cost,
        "recommended_cloud":
            "azure" if azure_cost < aws_cost else "aws"
    }
