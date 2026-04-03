# Faster Download Implementation Plan
Current Progress: 6/9

## Steps:
1. ✅ Plan approved by user.
2. ✅ Read app.py (already analyzed).
3. ✅ Update spotdl cmd: direct/64thr/96k/ultrafast/sponsorblock (app.py edited).
4. ✅ Increase max_retries=5.
5. ✅ Faster retry backoffs: 1.5-4s sleeps.
6. ⏳ Add metadata pre-fetch (optional 10-20% speedup).
7. ⏳ Test: python app.py + small playlist.
8. ⏳ Update TODO.
9. ⏳ attempt_completion.

**Next: Optional metadata pre-fetch & test**
