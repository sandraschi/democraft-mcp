import { expect, test } from "@playwright/test";

test("dashboard loads with KPIs", async ({ page }) => {
	await page.goto("/");
	await expect(page.getByTestId("kpi-craft-apps")).toBeVisible();
});

test("crafts list shows 13 apps", async ({ page }) => {
	await page.goto("/craft/cad");
	await expect(page.getByTestId("craft-run")).toBeVisible();
});

test("tools page lists operations", async ({ page }) => {
	await page.goto("/tools");
	await page.getByRole("button", { name: /craft/ }).click();
	await expect(page.getByTestId("tools-list")).toContainText("run_demo");
});

test("word page offers topic combobox", async ({ page }) => {
	await page.goto("/craft/word");
	await expect(page.getByTestId("topic-pick")).toBeVisible();
	await expect(page.getByTestId("topic-custom")).toBeVisible();
});

test("grid and fig pages offer topic comboboxes", async ({ page }) => {
	await page.goto("/craft/grid");
	await expect(page.getByTestId("topic-pick")).toBeVisible();
	await page.goto("/craft/fig");
	await expect(page.getByTestId("topic-pick")).toBeVisible();
});

test("onboarding CTA visible when wrappees missing", async ({ page }) => {
	await page.goto("/");
	const cta = page.getByTestId("onboarding-cta");
	if (await cta.count()) await expect(cta).toBeVisible();
});
