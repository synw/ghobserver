var app = new Vue({
	el: '#app',
	mixins: [vvMixin],
	data: {
		repos: [],
		repoInfos: {},
		activeView: {"slug": "repositories", "name": "Repositories"},
		activeRepo: {"slug": "all", "name": "All repositories"},
		viewClass: 'hidden',
		activeTimeframe: "3M",
		contentSrc: "",
		sidebarSrc: "",
		activity: {},
	},
	methods: {
		viewActivity: function() {
			this.activateView("activity", "Activity");
			this.resetFrames();
		},
		viewAllRepos: function() {
			this.activateView("repositories", "Repositories");
			this.activeRepo = {"slug": "all", "name": "All repositories"},
			this.loadReposContentView(this.activeTimeframe);
			this.repoInfos = {};
		},
		loadReposContentView: function(timeframe) {
			var base = "/static/charts/all_";
			var url = base+timeframe+".html";
			this.activeTimeframe = timeframe;
			this.ready(function(){
				var frame = document.getElementById("ifContent");
				frame.src = url;
			});
			this.loadSidebar(this.activeRepo, this.activeTimeframe);
		},
		viewRepo: function(reposlug) {
			var repo = this.getRepo(reposlug);
			// if page load
			if (repo === undefined) {return};
			this.activateView("repositories", "Repositories");
			this.getRepoData(reposlug);
			this.activeRepo = repo;
			this.loadContentView(repo, this.activeTimeframe);
		},
		getRepoData: function(reposlug) {
			function error(err) {
				console.log(err)
			}
			function action(data) {
				app.repoInfos = data;
				app.repoInfos.DiskUsage = humanFileSize(app.repoInfos.DiskUsage*1024, true);
				app.repoInfos.PushedAt = app.timeSince(app.repoInfos.PushedAt);
				app.repoInfos.CreatedAt = app.timeSince(app.repoInfos.CreatedAt);
			}
			var url = "http://localhost:8447/api/repository/"+reposlug;
			this.loadData(url, action, error);
		},
		timeSince: function(date) {
			return moment(date, "YYYYMMDD").fromNow()
		},
		activateView: function(slug, name) {
			this.activeView = {"slug": slug, "name": name};
			document.title = name+ ' - Gh';
		},
		loadContentView: function(repo, timeframe) {
			var slug = repo.slug.replace("-", "_");
			var base = "/static/charts/"+slug+"_";
			var url = base+timeframe+".html";
			this.activeTimeframe = timeframe;
			this.ready(function(){
				var frame = document.getElementById("ifContent");
				frame.src = url;
			});
			this.loadSidebar(repo, this.activeTimeframe);
		},
		resetFrames: function() {
			var url = "/static/blank.html";
			var frame = document.getElementById("ifSidebar");
			frame.src = url;
			var frame = document.getElementById("ifContent");
			frame.src = url;
		},
		loadSidebar: function(repo, timeframe) {
			var slug = repo.slug.replace("-", "_");
			var base = "/static/charts/"+slug+"_";
			var url = base+timeframe+"_sidebar.html";
			this.ready(function(){
				var frame = document.getElementById("ifSidebar");
				frame.src = url;
			});
		},
		getRepo: function(reposlug) {
			for (i=0;i<this.repos.length;i++) {
				if (this.repos[i].slug == reposlug) {
					return this.repos[i]
				}
			}
		},
		ready: function(callback) {
		    if (document.readyState!='loading') callback();
		    else if (document.addEventListener) document.addEventListener('DOMContentLoaded', callback);
		    else document.attachEvent('onreadystatechange', function(){
		        if (document.readyState=='complete') callback();
		    });
		},
	},
})