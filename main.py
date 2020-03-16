import requests
import csv
import os

'''
Format: 
Each market is a folder labeled with ID -- i.e. market2721
contains: 
A. "2721_meta.csv"
| "id", "name", "shortName", "image", "status", "url"  #only one
| "id", "name", "shortName", "image", "status", "dateEnd"  # for each contract
|
2. "contract4390.csv"
| "timeStamp", "lastTradePrice", "bestBuyYesCost", "bestBuyNoCost", "bestSellYesCost", "bestSellNoCost", "lastClosePrice"
|
Each contract file (i.e. 4390.csv)
'''


def get_latest_data(dest="data/", marketFileKey="id", contractFileKey="id"):
    response = requests.get("https://www.predictit.org/api/marketdata/all/")

    data = response.json()
    markets = data['markets']

    for market in markets:
        marketDir = dest + "market" + str(market[marketFileKey])
        if not os.path.exists(marketDir):
            os.makedirs(marketDir)

        if os.path.exists(marketDir + "/" + str(market[marketFileKey]) + "_meta.csv"):
            doesMetaExist = True
        else:
            doesMetaExist = False

        with open(marketDir + "/" + str(market[marketFileKey]) + "_meta.csv", "a") as meta_file:
            meta_writer = csv.writer(meta_file, delimiter=",")
            if not doesMetaExist:
                meta_writer.writerow(["id", "name", "shortName", "image", "status", "url"])
                meta_writer.writerow(
                    [market["id"], market["name"], market["shortName"], market["image"], market["status"],
                     market["url"]])
                meta_writer.writerow(["id", "name", "shortName", "image", "status", "dateEnd"])

            for contract in market["contracts"]:
                if not doesMetaExist:
                    meta_writer.writerow(
                        [contract["id"], contract["name"], contract["shortName"], contract["image"], contract["status"],
                         contract["dateEnd"]])

                if os.path.exists(marketDir + "/contract" + str(contract[contractFileKey]) + ".csv"):
                    doesContractExist = True
                else:
                    doesContractExist = False

                with open(marketDir + "/contract" + str(contract[contractFileKey]) + ".csv", "a") as contract_file:
                    contract_writer = csv.writer(contract_file, delimiter=",")
                    if not doesContractExist:
                        contract_writer.writerow(
                            ["timeStamp", "bestBuyYesCost", "bestBuyNoCost", "bestSellYesCost", "bestSellNoCost"])
                    contract_writer.writerow(
                        [market["timeStamp"], contract["bestBuyYesCost"], contract["bestBuyNoCost"],
                         contract["bestSellYesCost"], contract["bestSellNoCost"]])
                contract_file.close()
        meta_file.close()


get_latest_data()
