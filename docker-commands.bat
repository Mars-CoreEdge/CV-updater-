@echo off
REM Docker Commands for CV Updater Backend
REM Usage: docker-commands.bat [command]

if "%1"=="build" (
    echo Building Docker image...
    docker build -t cv-updater-backend ./backend
    goto :eof
)

if "%1"=="run" (
    echo Running Docker container...
    docker run -d --name cv-updater-backend -p 8000:8000 --env-file ./backend/.env cv-updater-backend
    goto :eof
)

if "%1"=="compose-up" (
    echo Starting with Docker Compose...
    docker-compose up -d
    goto :eof
)

if "%1"=="compose-down" (
    echo Stopping Docker Compose...
    docker-compose down
    goto :eof
)

if "%1"=="logs" (
    echo Showing container logs...
    docker logs -f cv-updater-backend
    goto :eof
)

if "%1"=="stop" (
    echo Stopping container...
    docker stop cv-updater-backend
    goto :eof
)

if "%1"=="remove" (
    echo Removing container...
    docker rm cv-updater-backend
    goto :eof
)

if "%1"=="restart" (
    echo Restarting container...
    docker restart cv-updater-backend
    goto :eof
)

if "%1"=="shell" (
    echo Opening shell in container...
    docker exec -it cv-updater-backend /bin/bash
    goto :eof
)

if "%1"=="status" (
    echo Container status:
    docker ps -a | findstr cv-updater-backend
    goto :eof
)

if "%1"=="clean" (
    echo Cleaning up Docker resources...
    docker-compose down
    docker system prune -f
    goto :eof
)

echo Usage: %0 {build^|run^|compose-up^|compose-down^|logs^|stop^|remove^|restart^|shell^|status^|clean}
echo.
echo Commands:
echo   build       - Build Docker image
echo   run         - Run container manually
echo   compose-up  - Start with Docker Compose
echo   compose-down- Stop Docker Compose
echo   logs        - Show container logs
echo   stop        - Stop container
echo   remove      - Remove container
echo   restart     - Restart container
echo   shell       - Open shell in container
echo   status      - Show container status
echo   clean       - Clean up Docker resources 