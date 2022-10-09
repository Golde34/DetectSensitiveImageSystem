/* Event */

// chrome.tabs.onActivated.addListener(function (activeInfo) {
//    chrome.tabs.get(activeInfo.tabId, function (tab) {
//       superCallBack(activeInfo.tabId, tab);
//    });
// });
chrome.tabs.onUpdated.addListener(function (tabId, changeInfo, updateTab) {
   chrome.tabs.query({ 'active': true }, function (activeTabs) {
      var activeTab = activeTabs[0];
      if (activeTab.id == updateTab.id) {
         var info = changeInfo;
         console.log("changeInfoUpdateListener: " + JSON.stringify(info));
         superCallBack(tabId, info);
      }
   });
});

/* Main */

function superCallBack(tabId, changeInfo) {
   if (changeInfo.status == "complete") {
      // chrome.tabs.executeScript({ code: "document.getElementsByTagName('body')[0].style.display = 'None'" });
      chrome.tabs.executeScript({ file: 'custom.js' });
      let data = [];
      const constantPercent = 70;
      var callback = function (results) {
         console.log('results of website: ' + results[0]);
         for (var i in results[0]) {
            if (results[0][i].toString().trim() == '') {
               continue;
            }
            data.push({
               url: results[0][i].toString()
            });
         }


         dataJson = JSON.stringify(data);
         getCurrentUrl();
         chrome.tabs.executeScript(tabId, {
            code: 'window.location.href'
         }, (urlRequested) => {
            console.log("dataJson: " + dataJson);
            callApi(dataJson, urlRequested).then(block => {
               chrome.tabs.executeScript({ code: "document.getElementsByTagName('body')[0].style.display = 'block'" });
               //Block by website domain
               for (const blockingSite of block.blockingSites) {
                  if (localStorage.getItem("currentUrl").includes(blockingSite)) {
                     chrome.tabs.executeScript({ file: 'block.js' });
                     console.log('Block successfully by blockingSites.');
                     break;
                  } else {
                     console.log('Block failed.');
                     continue;
                  }
               }
               //Block by percent
               console.log('block ')
               if (block.percent > constantPercent) {
                  chrome.tabs.executeScript({ file: 'block.js' });
                  console.log('Block successfully by percent.');
               } 
               console.log('----Block successfully----');
            }
            );
         });
      };
      chrome.tabs.executeScript(tabId, {
         code: 'Array.prototype.map.call(document.images, function (i) { return i.src; });'
      }, callback);
   }
}

console.log('Chrome Extension Run!');

var stringResponse = "response";
async function callApi(data, urlRequested) {
   let ip = statusIp();
   let resultResponse = {};
   const response = await fetch('http://127.0.0.1:8000/predict/', {
      method: 'POST', // or 'PUT'
      headers: {
         'Content-Type': 'application/json',
         'Authorization': ip,
         'Domain': urlRequested
      },
      body: data,
   }).then(response => response.json()) //server response
      .then(data => {

         console.log("data: ");
         console.log(data);
         if (data.length === 0 || data === 'undefined') {
            resultResponse = {
               "blockingSites": ["none"],
               "percent": 0,
            };
            chrome.tabs.executeScript({
               code: "document.getElementById('loading-icon').style.display = 'none';"
            });
         } else {
            var dataResponse = Object.entries(data);

            var blockingSites = dataResponse[0][1];
            var dataList = dataResponse[1][1];

            imgsToUpload = [];
            for (var i in dataList) {
               var index = dataList[i]['url'].lastIndexOf('/');
               if (dataList[i]['label'] === 'nude' || dataList[i]['label'] === 'sexy') {
                  var name = dataList[i]['url'].substring(index + 1, dataList[i]['url'].length - 3);
                  imgsToUpload.push(name);
               }
            }

            //percent nude page > 90%
            let percent = imgsToUpload.length / dataList.length * 100;

            chrome.tabs.executeScript({
               code: 'var imgsToUpload = "' + imgsToUpload + '";'
            }, function () {
               chrome.tabs.executeScript({ file: 'uploadScript.js' });
            });

            resultResponse.percent = percent;
            resultResponse.blockingSites = blockingSites;
            console.log(resultResponse);
         }
      }
      )
      .catch(console.error);
   return resultResponse;
}

function statusIp() {
   var statusIp = localStorage.getItem("statusIp");
   if (statusIp === "OK") {
      ip = localStorage.getItem("key");
      console.log(ip);
   } else if (statusIp === "Deleted") {
      ip = "";
      console.log(ip);
   }
   return ip;
}

function getCurrentUrl() {
   chrome.tabs.query({ active: true, currentWindow: true }, tabs => {
      let url = tabs[0].url;
      localStorage.setItem("currentUrl", url);
   });
}