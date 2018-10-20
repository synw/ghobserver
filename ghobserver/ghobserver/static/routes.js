page("/", function(ctx, next) { app.viewActivity() });
page("/repositories", function(ctx, next) { app.viewAllRepos() });
page("/repository/:reposlug", function(ctx, next) { app.viewRepo(ctx.params.reposlug); });
page();