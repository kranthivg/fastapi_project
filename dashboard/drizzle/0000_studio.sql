CREATE TABLE IF NOT EXISTS studio_posts (id INTEGER PRIMARY KEY AUTOINCREMENT, workspace TEXT NOT NULL, owner_id INTEGER NOT NULL, title TEXT NOT NULL, content TEXT NOT NULL, published INTEGER NOT NULL DEFAULT 1, created TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);
--> statement-breakpoint
CREATE INDEX studio_posts_workspace ON studio_posts(workspace, id);
--> statement-breakpoint
CREATE TABLE IF NOT EXISTS studio_votes (workspace TEXT NOT NULL, user_id INTEGER NOT NULL, post_id INTEGER NOT NULL REFERENCES studio_posts(id) ON DELETE CASCADE, PRIMARY KEY(workspace,user_id,post_id));
