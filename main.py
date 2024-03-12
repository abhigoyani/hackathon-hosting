from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from dotenv import load_dotenv

from routers import auth, user, hackathon, project, organizer, search, admin

import uvicorn

load_dotenv()


app = FastAPI()

app.mount("/image-content", StaticFiles(directory="project_images"),
          name="project_images")


app.include_router(auth.router)
app.include_router(user.router)
app.include_router(hackathon.router)
app.include_router(project.router)
app.include_router(organizer.router)
app.include_router(search.router)
app.include_router(admin.router)


if __name__ == "__main__":
    uvicorn.run(app)
