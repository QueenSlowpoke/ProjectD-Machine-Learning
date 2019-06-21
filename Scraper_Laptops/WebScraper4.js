/* 
https://www.youtube.com/watch?v=LoziivfAAjE 

The initial file is copied, because we want to use most of the same stuff.

Use the fs module (comes with node) to convert all the data to a .csv file
(and so you don't have to install anything, you just have to call it in).
Create a variable (in this case called writeStream) to open up a stream to
write. The variable is set to the fs module createWriteStream('filename that
you want to use')
*/

const request = require('request');
const cheerio = require('cheerio');
const fs = require('fs');
const writeStream = fs.createWriteStream('Laptops.csv');

var brands = ['Acer', 'Advent', 'Alienware', 'Apple', 'Asus','Dell', 'Google',
              'HP', 'Huawei', 'Lenovo', 'Microsoft', 'Nokia', 'Packard Bell',
              'Panasonic', 'Razer', 'Samsung', 'Sony', 'Toshiba'];

var links = ['https://www.ebay.com/b/PC-Laptops-Netbooks/177/bn_317584',
             'https://www.ebay.com/b/PC-Laptops-Netbooks/177/bn_317584?_pgn=2', 
             'https://www.ebay.com/b/PC-Laptops-Netbooks/177/bn_317584?_pgn=3',
             'https://www.ebay.com/b/PC-Laptops-Netbooks/177/bn_317584?_pgn=4',
             'https://www.ebay.com/b/PC-Laptops-Netbooks/177/bn_317584?_pgn=5',
             'https://www.ebay.com/b/PC-Laptops-Netbooks/177/bn_317584?_pgn=6'];
var id = 0;
var linkIndex = 1;

// Headers
writeStream.write(`Id, Title, Brand, Image, Price \n`);

links.forEach(function(entry){ 
    request(entry, (error, response, html) => {
        if(!error && response.statusCode == 200) {
            const $ = cheerio.load(html);

            $('.s-item').each((index, el) => {
                const title = $(el)
                 .find('.s-item__title')
                 .text()
                 // Use replace to get rid of all the shitty whitespaces.
                 .replace(/\s\s+/g, '');

                var title2 = title;
                if (title2.includes(',') == true){
                    title2 = '';
                } 
                if (title2.includes('New Listing') == true){
                    title2 = title2.replace('New Listing', '');
                } else if (title.includes('New') == true){
                    title2 = title2.replace('New', '');
                }

                var brand = '';
                var brand_search = title;
                var array_index = 0;
                brands.forEach(function(brand_names){
                    var brand_find = brand_search.includes(brand_names);
                    if (brand_find == true){
                        brand = brands[array_index];
                    }
                    array_index += 1;
                })
             
                const image = $(el)
                 .find('.s-item__image-img')
                 .attr('data-src');
 
                const price = $(el)
                 .find('.s-item__price')
                 .text();
                
                var price2 = price;
                if(price2.includes('t')){
                    price2 = price2.substring(0, price2.indexOf('t'));
                }
                if (price2.includes(',')){
                    price2 = '';
                }
 
                 /*if (image != undefined && (title2 != '' || price2 != '' || brand != '') || id > 150){
                     id = id + 1;
                     //console.log(id, title2, brand, image, price2);
                     console.log(id, brand);
                     //writeStream.write(`${id},${title2},${brand},${image},${price2} \n`);
                 }*/

                 if (image != undefined){
                     if (title2 != ''){
                         if (price2 != ''){
                             if (brand != ''){
                                 if (id < 150){
                                     id += 1;
                                     console.log(id, title2);
                                     writeStream.write(`${id},${title2},${brand},${image},${price2} \n`);
                                 }
                             }
                         }
                     }
                 }
                
            });
            
    }
    // Visual check to see / know when the file is ready.
    console.log('link',linkIndex ,'of', links.length, 'Finished AF');
    linkIndex += 1;
});

});