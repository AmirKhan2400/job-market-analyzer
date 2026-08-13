# from fastapi import FastAPI

# from job_market_analyzer.api.routes import router

# app = FastAPI(
#     title="AI Job Market Analyzer",
#     version="0.1.0",
# )

# app.include_router(router)

from pathlib import Path

from job_market_analyzer.services.profile_loader import load_profile

profile = load_profile(Path("examples/profile.yaml"))

print(profile)

print("profile.skills: ", profile.skills)
print("profile.target_roles: ", profile.target_roles)
