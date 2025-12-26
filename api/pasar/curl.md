# ✅ GET: Get all marketplace items (working)
curl -X GET http://nusasawit.com/api/pasar/ \
  -H "X-APP-KEY: NUSA-APP-KEY-15c9f3fd8c8943f8a3bcd871df1b6f49"

# ❌ POST: Create new marketplace item (requires photo files)
curl -X POST http://localhost:8000/api/pasar/ \
  -H "Content-Type: multipart/form-data" \
  -H "X-APP-KEY: NUSA-APP-KEY-15c9f3fd8c8943f8a3bcd871df1b6f49" \
  -H "X-EMAIL: seller@example.com" \
  -H "X-PHONE: +62812345678" \
  -F "title=Laptop Gaming" \
  -F "description=Laptop gaming kondisi bagus" \
  -F "price=15000000" \
  -F "photo_1=@/path/to/image.jpg"

# ✅ GET: Get specific marketplace item (requires existing ID)
curl -X GET http://localhost:8000/api/pasar/{existing_id}/ \
  -H "X-APP-KEY: NUSA-APP-KEY-15c9f3fd8c8943f8a3bcd871df1b6f49"

# ✅ GET: Get comments for specific item (requires existing ID)
curl -X GET http://localhost:8000/api/pasar/{existing_id}/comments/ \
  -H "X-APP-KEY: NUSA-APP-KEY-15c9f3fd8c8943f8a3bcd871df1b6f49"

# ✅ POST: Add comment to item (requires existing ID)
curl -X POST http://localhost:8000/api/pasar/{existing_id}/comments/ \
  -H "Content-Type: application/json" \
  -H "X-APP-KEY: NUSA-APP-KEY-15c9f3fd8c8943f8a3bcd871df1b6f49" \
  -H "X-EMAIL: buyer@example.com" \
  -H "X-PHONE: +628987654321" \
  -d '{"message": "This is a comment"}'

# ✅ POST: Mark item as sold (requires existing ID)
curl -X POST http://localhost:8000/api/pasar/{existing_id}/mark-sold/ \
  -H "Content-Type: application/json" \
  -H "X-APP-KEY: NUSA-APP-KEY-15c9f3fd8c8943f8a3bcd871df1b6f49" \
  -H "X-EMAIL: seller@example.com" \
  -H "X-PHONE: +62812345678" \
  -d '{"is_sold": true}'