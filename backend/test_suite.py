import urllib.request
import urllib.parse
import json
import os

BASE_URL = "http://localhost:8000"

def search(query):
    req = urllib.request.Request(
        f"{BASE_URL}/api/search",
        data=json.dumps({"query": query}).encode('utf-8'),
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode('utf-8'))

def test_evidence(frame_url):
    req = urllib.request.Request(f"{BASE_URL}{frame_url}")
    with urllib.request.urlopen(req) as resp:
        data = resp.read()
        return resp.status, len(data)

def set_memory(key, value):
    req = urllib.request.Request(
        f"{BASE_URL}/api/memory",
        data=json.dumps({"key": key, "value": value}).encode('utf-8'),
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode('utf-8'))

def run_all_tests():
    print("=" * 70)
    print("EXECUTING COMPLETE MVP TEST SUITE")
    print("=" * 70)
    
    test_results = []
    
    # Test 1: Simple object query ("Show me a car")
    q1 = "Show me a car"
    res1 = search(q1)
    has_car = len(res1.get("results", [])) > 0 and res1["results"][0]["verified"]
    status1 = "PASS" if has_car else "FAIL"
    test_results.append(("TEST 01: Simple Object (Car)", q1, "MATCH FOUND (Camera 01 / 02)", f"Found {len(res1.get('results',[]))} results", status1))
    print(f"TEST 01: {q1} -> {status1} (Results: {len(res1.get('results',[]))})")
    if has_car:
        r = res1["results"][0]
        print(f"  -> Cam: {r['camera_name']}, Time: {r['timestamp']}, Score: {r['score']*100:.1f}%, Frame: {r['frame_url']}")
        
    # Test 2: Second object query ("Show me a white car")
    q2 = "Show me a white car"
    res2 = search(q2)
    has_wcar = len(res2.get("results", [])) > 0 and res2["results"][0]["verified"]
    status2 = "PASS" if has_wcar else "FAIL"
    test_results.append(("TEST 02: Attribute Query (White Car)", q2, "MATCH FOUND (Camera 01)", f"Found {len(res2.get('results',[]))} results", status2))
    print(f"TEST 02: {q2} -> {status2}")
    if has_wcar:
        r = res2["results"][0]
        print(f"  -> Cam: {r['camera_name']}, Time: {r['timestamp']}, Score: {r['score']*100:.1f}%, Frame: {r['frame_url']}")

    # Test 3: Person query ("Show me a person")
    q3 = "Show me a person"
    res3 = search(q3)
    has_person = len(res3.get("results", [])) > 0 and res3["results"][0]["verified"]
    status3 = "PASS" if has_person else "FAIL"
    test_results.append(("TEST 03: Person Query", q3, "MATCH FOUND (Camera 02 / 03)", f"Found {len(res3.get('results',[]))} results", status3))
    print(f"TEST 03: {q3} -> {status3}")
    if has_person:
        r = res3["results"][0]
        print(f"  -> Cam: {r['camera_name']}, Time: {r['timestamp']}, Score: {r['score']*100:.1f}%, Frame: {r['frame_url']}")

    # Test 4: Negative query (Green Car - does not exist)
    q4 = "Show me a green car"
    res4 = search(q4)
    neg_pass1 = len(res4.get("results", [])) == 0
    status4 = "PASS" if neg_pass1 else "FAIL (False Positive Returned!)"
    test_results.append(("TEST 04: Negative Query (Green Car)", q4, "NO VERIFIED MATCH FOUND", f"Returned {len(res4.get('results',[]))} results", status4))
    print(f"TEST 04: {q4} -> {status4}")
    
    # Test 5: Red-car query (Red Car - does not exist in clear footage)
    q5 = "did a red car passed the main gate?"
    res5 = search(q5)
    neg_pass2 = len(res5.get("results", [])) == 0
    status5 = "PASS" if neg_pass2 else "FAIL (False Positive Returned!)"
    test_results.append(("TEST 05: Red-car / False Attribute Query", q5, "NO VERIFIED MATCH FOUND", f"Returned {len(res5.get('results',[]))} results", status5))
    print(f"TEST 05: {q5} -> {status5}")

    # Test 6: Negative query (Bicycle - does not exist)
    q6 = "Show me a bicycle"
    res6 = search(q6)
    neg_pass3 = len(res6.get("results", [])) == 0
    status6 = "PASS" if neg_pass3 else "FAIL (False Positive Returned!)"
    test_results.append(("TEST 06: Negative Query (Bicycle)", q6, "NO VERIFIED MATCH FOUND", f"Returned {len(res6.get('results',[]))} results", status6))
    print(f"TEST 06: {q6} -> {status6}")

    # Test 7: Camera correctness (Workers in zone -> Camera 03)
    q7 = "Show me workers in the zone"
    res7 = search(q7)
    cam3_pass = len(res7.get("results", [])) > 0 and res7["results"][0]["camera_id"] == "camera_03"
    status7 = "PASS" if cam3_pass else "FAIL"
    test_results.append(("TEST 07: Camera Correctness (Workers -> Cam 03)", q7, "Camera 03 match", f"Cam: {res7.get('results', [{}])[0].get('camera_id')}", status7))
    print(f"TEST 07: {q7} -> {status7}")
    if cam3_pass:
        r = res7["results"][0]
        print(f"  -> Cam: {r['camera_name']}, Time: {r['timestamp']}, Score: {r['score']*100:.1f}%, Frame: {r['frame_url']}")

    # Test 8: Timestamp correctness
    t_pass = len(res1.get("results", [])) > 0 and res1["results"][0]["timestamp"] != "00:00:00"
    status8 = "PASS" if t_pass else "FAIL"
    test_results.append(("TEST 08: Timestamp Correctness", "Non-zero timestamp verification", "Valid MM:SS timestamp grounded in video", f"Timestamp: {res1.get('results', [{}])[0].get('timestamp')}", status8))
    print(f"TEST 08: Timestamp Correctness -> {status8}")

    # Test 9: Evidence loading
    if res1.get("results"):
        f_url = res1["results"][0]["frame_url"]
        http_code, byte_len = test_evidence(f_url)
        e_pass = (http_code == 200 and byte_len > 1000)
        status9 = "PASS" if e_pass else "FAIL"
        test_results.append(("TEST 09: Evidence Frame Resolution", f_url, "HTTP 200 + readable JPEG bytes", f"HTTP {http_code}, {byte_len} bytes", status9))
        print(f"TEST 09: Evidence loading {f_url} -> {status9} ({byte_len} bytes)")

    # Test 10: Missing evidence error handling
    try:
        req_missing = urllib.request.Request(f"{BASE_URL}/api/evidence/frames/non_existent_frame.jpg")
        urllib.request.urlopen(req_missing)
        status10 = "FAIL"
    except urllib.error.HTTPError as e:
        status10 = "PASS" if e.code == 404 else "FAIL"
    test_results.append(("TEST 10: Missing Evidence 404 Handling", "/api/evidence/frames/non_existent.jpg", "HTTP 404 Not Found", f"Status 404 verified", status10))
    print(f"TEST 10: Missing evidence handling -> {status10}")

    # Test 11: Clarify-once memory write & read
    set_memory("main gate", "camera_01")
    q11 = "did a car enter the main gate?"
    res11 = search(q11)
    mem_pass = len(res11.get("results", [])) > 0 and res11["results"][0]["camera_id"] == "camera_01"
    status11 = "PASS" if mem_pass else "FAIL"
    test_results.append(("TEST 11: Clarify-once Memory Grounding", q11, "Restricted to Camera 01 (main gate)", f"Returned cam: {res11.get('results', [{}])[0].get('camera_id')}", status11))
    print(f"TEST 11: Clarify-once memory -> {status11}")

    # Test 12: Multiple consecutive searches
    consec_pass = True
    for test_q in ["Show me a car", "Show me a person", "Show me a green car", "Show me a white car"]:
        try:
            search(test_q)
        except Exception:
            consec_pass = False
    status12 = "PASS" if consec_pass else "FAIL"
    test_results.append(("TEST 12: Consecutive Multiple Searches", "4 sequential queries", "All succeed without crash", "Backend stable", status12))
    print(f"TEST 12: Multiple consecutive searches -> {status12}")

    print("\n" + "=" * 70)
    print("FINAL TEST SUMMARY MATRIX:")
    print("=" * 70)
    for row in test_results:
        print(f"{row[0]:<40} | {row[4]}")
    print("=" * 70)

if __name__ == "__main__":
    run_all_tests()
