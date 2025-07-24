echo "=== docker compose down -vv ==="
docker compose down -vv

sleep 1
echo ""
echo ""
echo "=== system prune==="
docker system prune 