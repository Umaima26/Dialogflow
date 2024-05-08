from flask import Flask, request, jsonify
import requests
import datetime

app = Flask(__name__)


@app.route("/webhook", methods=["POST"])

def webhook():

    data = request.get_json(silent=True)

    intent_name = data["queryResult"]["intent"]["displayName"]

    if (data is None or "queryResult" not in data or "parameters" not in data["queryResult"]):
        return jsonify({"error": "Invalid request payload"}), 400

    if intent_name == "Process OrderID Intent":

        orderID = data["queryResult"]["parameters"]["orderID"]

        if orderID is None:
            return jsonify({"error": "Order ID not provided"}), 400

        apiUrl = "https://orderstatusapi-dot-organization-project-311520.uc.r.appspot.com/api/getOrderStatus"
        requestBody = {"orderId": orderID}

        try:
            response = requests.post(apiUrl, json=requestBody)
            shipmentDate = response.json()["shipmentDate"]
            formattedDate = formatShipmentDate(shipmentDate)

            fulfillmentText = f"Your order {orderID} will be shipped on {formattedDate}."
            responseBody = {"fulfillmentText": fulfillmentText}
            return jsonify(responseBody), 200

        except Exception as e:
            print(f"Error fetching order status: {e}")
            return jsonify({"fulfillmentText": "Error fetching order status"}), 500


def formatShipmentDate(shipmentDate):
    return datetime.datetime.strptime(shipmentDate, "%Y-%m-%dT%H:%M:%S.%fZ").strftime(
        "%A, %d %B %Y"
    )


if __name__ == "__main__":
    app.run(debug=True)
