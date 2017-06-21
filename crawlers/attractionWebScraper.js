require('events').EventEmitter.prototype._maxListeners = 0;
const fs = require('fs');
const cheerio = require('cheerio');
const https = require('https');
const mongo = require('./mongo.js');
const mongo_url = 'mongodb://localhost:27017/webScraper';
const crypto = require('crypto');

https.globalAgent.maxSockets = 100;

function getPageData(url, callback){
	var pageData;
	const request = https.get(url, function(response){
		response.on('data', function(chunk){
			pageData += chunk;
		});
		response.on('end', function(){
			if(pageData != undefined){
				callback(cheerio.load(pageData));
				request.end();
			};
		});
	});
	request.on('error', function(err){
		console.log(err);
	});
}

function getUrl(callback){
	JSON.parse(fs.readFileSync('attractionUrls.json', 'utf8'))
	.map((elem)=>
		elem.url)
	.map((url)=>
		getPageData(url, function(pageData){
			callback(url);
			try{
			lastPageIndex = pageData('a.pageNum.taLnk').toArray().pop()['attribs']['data-offset']/10;
			Array.apply(null, {length: lastPageIndex})
			.map((elem, index)=>
				(index + 1)*10).map((pageIndex)=>
				callback(url.replace('-Reviews-', `-Reviews-or${pageIndex}-`))
				);
			}
			catch(err){
				console.log(`error on => ${url}`)
			};
			})
		);
};

function getComments(callback){
	getUrl(function(url){
		getPageData(url, function(pageData){
			comments = pageData('div.reviewSelector').find('p.partial_entry').contents().toArray()
			.map((elem)=>
				elem['data'])
			.filter((elem)=>
				elem != undefined && elem.length != 0 && elem != '\n');
			ratings = pageData('div.reviewSelector').find('span.ui_bubble_rating').toArray()
			.map((elem)=>
				elem['attribs']['class'])
			.map((elem)=>
				parseInt(elem.match(/\d/g)))
			if(comments.length == ratings.length){
				docs = Array.apply(null, {length: comments.length}).map((elem, index)=>
					JSON.parse(JSON.stringify({'_id': crypto.createHash('md5').update(comments[index].toString()).digest('base64'), 'comment': comments[index], 'rating': ratings[index]})));
				callback(docs);
			};
		});
	});
};

getComments(function(docs){
	if(docs.length != 0){
		mongo.conn(mongo_url, function(db){
			mongo.insert(db, 'tripAdvisorAttraction', docs, function(result){
				console.log(result);
				db.close();
			});
		});
	};
});