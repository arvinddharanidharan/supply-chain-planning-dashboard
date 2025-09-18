# Automated ETL Pipeline Setup (100% FREE)

## Architecture
```
GitHub Actions (6 AM daily) → ETL Script → PostgreSQL (Neon) → Streamlit App
```

## 1. Free PostgreSQL Database Setup

### Sign up for Neon.tech (FREE)
1. Go to https://neon.tech
2. Sign up with GitHub account
3. Create new project: "supply-chain-db"
4. Copy connection details

### Update secrets.toml
```toml
DB_HOST = "ep-xxx-xxx.us-east-2.aws.neon.tech"
DB_NAME = "supply_chain_db"
DB_USER = "your-username"
DB_PASSWORD = "your-password"
DB_PORT = "5432"
```

## 2. GitHub Repository Setup

### Push to GitHub
```bash
git add .
git commit -m "Add automated ETL pipeline"
git push origin main
```

### Add GitHub Secrets
Go to: Repository → Settings → Secrets and variables → Actions

Add these secrets:
- `DB_HOST`: Your Neon hostname
- `DB_NAME`: supply_chain_db
- `DB_USER`: Your Neon username
- `DB_PASSWORD`: Your Neon password
- `DB_PORT`: 5432

## 3. Manual Testing

### Test ETL Pipeline
```bash
pip install psycopg2-binary sqlalchemy
python etl_data_generator.py
```

### Test Database Connection
```bash
python -c "from database import get_db_connection; print('Connected!' if get_db_connection() else 'Failed!')"
```

## 4. Automation Schedule

- **Daily at 6:00 AM UTC**: New data generated
- **Business Logic**: Supplier trends, seasonal patterns
- **Data Growth**: 10-50 new orders daily
- **Fallback**: CSV files if database fails

## 5. Free Tier Limits

### Neon.tech FREE
- 10 GB storage
- 1 database
- Unlimited queries

### GitHub Actions FREE
- 2,000 minutes/month
- Daily ETL uses ~2 minutes
- 30x daily runs = 60 minutes/month

## 6. Business Intelligence Features

### Automated Data Patterns
- Supplier performance trends
- Seasonal demand variations
- ABC classification evolution
- Stock level optimization

### Real-time Updates
- Fresh data every morning
- Automatic email alerts
- Performance tracking
- Compliance monitoring

## 7. Monitoring

### Check ETL Status
- GitHub Actions tab shows daily runs
- Email notifications on failures
- CSV backup always available

### Data Quality
- Incremental data validation
- Business rule enforcement
- Trend analysis
- Anomaly detection

## 8. Scaling Options

### If you outgrow free tiers:
- **Neon Pro**: $19/month (100GB)
- **GitHub Pro**: $4/month (3,000 minutes)
- **Alternative**: Railway, Supabase, PlanetScale

## 9. Manual Triggers

### Run ETL Anytime
1. Go to GitHub Actions
2. Select "Daily ETL Pipeline"
3. Click "Run workflow"
4. Data updates in ~2 minutes

## 10. Troubleshooting

### Database Connection Issues
```python
# Test connection
from database import get_db_connection
conn = get_db_connection()
print("Connected!" if conn else "Check secrets.toml")
```

### ETL Pipeline Failures
- Check GitHub Actions logs
- Verify database credentials
- Ensure CSV fallback works
- Monitor free tier limits

This setup provides enterprise-grade ETL automation at zero cost!