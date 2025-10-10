from sqlalchemy import Column, String, Integer, DateTime, Enum, Float
from sqlalchemy.orm import declarative_base
from datetime import datetime
import enum

Base = declarative_base()

class JobStatus(enum.Enum):
uploaded = "uploaded"
processing = "processing"
preview_ready = "preview_ready"
awaiting_payment = "awaiting_payment"
paid = "paid"
done = "done"
failed = "failed"

class Job(Base):
__tablename__ = "jobs"
id = Column(String, primary_key=True)
original_filename = Column(String)
upload_key = Column(String) # s3 key
preview_key = Column(String) # s3 key
output_key = Column(String) # s3 key
lufs = Column(Float)
status = Column(Enum(JobStatus), default=JobStatus.uploaded)
created_at = Column(DateTime, default=datetime.utcnow)

class Payment(Base):
__tablename__ = "payments"
id = Column(String, primary_key=True) # Stripe session id
job_id = Column(String)
amount = Column(Integer)
currency = Column(String)
created_at = Column(DateTime, default=datetime.utcnow)
