//convert String imgsToUpload to list of number
if (imgsToUpload.length == 0) {
   console.log("Do nothing");
} else {
   var listCensore = imgsToUpload.split(",");

   //get all images from tab web
   var images = document.querySelectorAll("img");
   var srcArray = Array.from(images).map(function (image) {
      return image.currentSrc;
   });

   //define nude images in tab web
   replaceImgs = [];
   count = 0;
   for (img of srcArray) {
      for (var k = 0; k < listCensore.length; k++) {
         if (img.includes(listCensore[k])) {
            replaceImgs.push(img);
         }
      }
      count++;
   }

   //upload server image to nude image
   for (var i = 0; i < images.length; i++) {
      for (var j = 0; j < listCensore.length; j++) {
         if (images[i].src.includes(listCensore[j])) {
            images[i].src = images[i].src.replace(replaceImgs[j], "https://thumbs.dreamstime.com/b/kids-not-allowed-coro-covid-can-be-used-no-entry-children-shopping-malls-office-lobby-stores-kids-not-193397344.jpg");
            console.log('upload ' + i);
            console.log(typeof (srcArray));
         }
      }
   }

   // console.log(replaceImgs);
   // console.log(listCensore);
   // console.log(typeof(images[1]));
   // console.log(images[1]);

}
var element = document.getElementById('loading-icon');
element.parentNode.removeChild(element);
