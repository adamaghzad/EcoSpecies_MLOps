from .common import BASE, save_json, digest
from .data import read_validate

def main():
    df=read_validate(BASE/"data/penguins.csv")
    report={"rows":len(df),"sha256":digest(BASE/"data/penguins.csv"),"missing":df.isna().sum().to_dict(),"classes":df.species.value_counts().to_dict()}
    save_json(BASE/"reports/data_validation.json",report)
    print(report)
if __name__=="__main__":main()
