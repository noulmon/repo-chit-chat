from data_ingestion.pipeline import run_pipeline


if __name__ == "__main__":
    data = run_pipeline('DataTalksClub', 'faq')
    print(data)
