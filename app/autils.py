from fastapi import status, HTTPException



def http_exception(status_codes: status, details: str):
  raise HTTPException(status_code= status_codes, detail=details)