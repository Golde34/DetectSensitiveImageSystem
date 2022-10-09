var storeIp;
var localIp = localStorage.getItem("key");

window.onload = function () {
	let button = document.getElementById('ip_json');
	var mess = document.getElementById('mess');
	if (localIp === "" || localIp === null || localIp == 'undefined') {
		button.innerHTML = "Submit";
		button.value = "Submit";
	} else {
		button.innerHTML = "Delete";
		button.value = "Delete";
	}

	if (button.innerHTML === "Submit") {
		button.onclick = function () {
			var input = document.getElementById("ip");
			localStorage.setItem("key", input.value);
			storeIp = localStorage.getItem("key");
			console.log("store local: " + storeIp);
			mess.innerHTML = "Submit successfully";
			let data = { key: storeIp };
			dataJson = JSON.stringify(data);
			callApi(dataJson).then(result => {
				console.log(result);
			});
		}
	}

	if (button.innerHTML === "Delete") {
		let key = localStorage.getItem("key");
		document.getElementById("ip").value = key;
		console.log(key);
		button.onclick = function () {
			localStorage.setItem("key", "");
			console.log("Delete");
			document.getElementById("ip").value = key;
			console.log(key);
			mess.innerHTML = "Delete successfully";
			deleteIp();
		}
	}
}

function callApi(data) {
	fetch('http://127.0.0.1:8000/api/checkManageAccount/', {
		method: 'POST', // or 'PUT'
		headers: {
			'Content-Type': 'application/json',
		},
		body: data,
	}).then((result) => {
		console.log(result["statusText"]);
		localStorage.setItem("statusIp", result["statusText"]);
		console.log("Pushed key to server");
	}).then((err) => {
		console.log("error", err)
	})
}

function deleteIp() {
	localStorage.setItem("statusIp", "Deleted");
	console.log(localStorage.getItem("statusIp"));
	console.log("Deleted key in extension");
	console.log(localStorage.getItem("key"));
}
