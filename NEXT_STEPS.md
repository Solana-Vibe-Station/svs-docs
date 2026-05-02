# Next Steps: Push to GitHub and Connect GitBook Git Sync

The local repo in this folder is initialized, has an initial commit on `main`, and is ready to push. This file walks you through getting it onto GitHub and wiring it up to your existing GitBook space at [docs.solanavibestation.com](https://docs.solanavibestation.com).

## 1. Create the empty GitHub repository

1. Go to https://github.com/new while signed in as the account that owns Solana Vibe Station's GitHub presence.
2. Repository name: `svs-docs` (recommended — matches the local folder name).
3. Owner: your personal account or your `solanavibestation` organization, whichever GitBook will sync from.
4. Visibility: **Private** is fine; GitBook Git Sync supports both public and private repos. Make it Public if you want the docs source open to the community.
5. **Do not** initialize with a README, license, or `.gitignore` — the local repo already has those, and an empty remote keeps the first push simple.
6. Click **Create repository** and leave the page open — you'll need the URL on the next page.

## 2. Push the local repo

Open a terminal in `C:\Users\ajohn\Documents\Projects\Solana Vibe Station\gitbooks\svs-docs` and run:

```bash
# Replace <owner> with your GitHub username or org
git remote add origin https://github.com/<owner>/svs-docs.git
git push -u origin main
```

If you'd rather use SSH:

```bash
git remote add origin git@github.com:<owner>/svs-docs.git
git push -u origin main
```

You should see all 71 files upload in a single push. Refresh the GitHub page to confirm.

## 3. Connect GitBook Git Sync

1. Open [GitBook](https://app.gitbook.com), navigate to your `docs.solanavibestation.com` space.
2. Click the space's **gear icon** → **Synchronize with Git**.
3. Choose **GitHub** and authorize the GitBook app for the account/org that owns the new repo.
4. Select the `svs-docs` repository and the `main` branch.
5. **Project directory**: set to `docs/` (this is the folder GitBook treats as the root of your content tree).
6. Choose the sync direction:
   - **Recommended:** "GitBook ↔ GitHub" (bidirectional). Edits in either place propagate.
   - "GitHub → GitBook" (one-way) is fine if you want the repo to be the only source of truth.
7. Confirm and run the initial sync. GitBook will read `docs/SUMMARY.md` and rebuild the navigation from the new structure.

If you're nervous about overwriting the live site, **clone your existing GitBook space first** (Space settings → Duplicate) and connect Git Sync to the duplicate. Verify it looks right, then swap the production space over.

## 4. Verify OpenAPI specs render

In any GitBook page, you can embed an OpenAPI spec from the same repo with a block like:

```
{% openapi src="../api-specs/svs-api.yaml" path="/metadata" method="post" %}
{% endopenapi %}
```

Open `docs/svs-api/token-metadata.md`, `token-price.md`, and `mint-info.md` and confirm GitBook renders the API blocks. If a block doesn't show, check that the `path` and `method` match an entry in `api-specs/svs-api.yaml`.

## 5. Day-to-day workflow from here on

**Adding or changing an API endpoint:**
1. Edit the relevant YAML in `api-specs/`.
2. (If a new endpoint) add an `{% openapi %}` block in the appropriate `docs/svs-api/*.md` page.
3. Add a one-line entry to `docs/svs-api/changelog.md`.
4. `git add . && git commit -m "..." && git push`.
5. GitHub Actions lints the spec; GitBook picks up the change within a couple of minutes.

**Adding a new docs page:**
1. Create the `.md` file under the right `docs/<section>/` folder.
2. Add a line in `docs/SUMMARY.md` to put it in the sidebar.
3. Commit and push.

**Editing existing pages:** just edit the markdown and push. GitBook resyncs automatically.

## 6. Cleanup once you're confident

- The `legacy-openapi/` folder is preserved as a rollback point. Once the new docs site is live and verified, delete the folder in a follow-up commit (`git rm -r legacy-openapi && git commit -m "Remove archived per-method specs"`).
- Inside GitBook, set up redirects from any old URLs your customers may have bookmarked — see Phase 2 of `SVS_Docs_Reorganization_Plan.docx` in the parent folder for the list of recommended redirects.

## 7. Optional: invite collaborators

If your co-founders or contractors need to edit docs:
- **GitHub side:** repo Settings → Collaborators → Add people.
- **GitBook side:** Space settings → Members → invite by email.

Either side's edits will sync through the other.
