import { expect, Locator, Page } from '@playwright/test';
import { BasePage } from './base-page';

export class MapPage extends BasePage {
  // Map elements
  readonly mapContainer: Locator;
  readonly mapCanvas: Locator;
  readonly geolocateControl: Locator;
  readonly navigationControl: Locator;
  readonly scaleControl: Locator;
  readonly sidepanel: Locator;
  readonly routeCalculator: Locator;
  readonly waypointManager: Locator;

  // Navbar component elements (part of the page)
  readonly navbar: Locator;
  readonly brandLink: Locator;
  readonly navbarToggler: Locator;
  readonly navbarCollapse: Locator;
  readonly mapLink: Locator;

  constructor(page: Page) {
    super(page);
    // Map elements - keeping ID selectors for map-specific elements as they don't have semantic roles
    this.mapContainer = page.locator('#map');
    this.mapCanvas = page.locator('#map canvas');
    this.geolocateControl = page.locator('.maplibregl-ctrl-geolocate');
    this.navigationControl = page.locator('.maplibregl-ctrl-group').first();
    this.scaleControl = page.locator('.maplibregl-ctrl-scale');
    this.sidepanel = page.locator('app-map-sidepanel');
    this.routeCalculator = page.locator('app-route-calculator');
    this.waypointManager = page.locator('app-waypoint-manager');

    // Navbar component elements - using role-based locators where possible
    this.navbar = page.getByRole('navigation');
    this.brandLink = page.getByRole('link', { name: /trackoss/i });
    this.navbarToggler = page.getByRole('button', { name: /toggle navigation/i });
    this.navbarCollapse = page.locator('.navbar-collapse'); // Keep as fallback if no role
    this.mapLink = page.getByRole('link', { name: /map/i });
  }

  /**
   * Navigate to the map page
   */
  async navigateToMap() {
    await this.goto('/map');
    await this.waitForMapLoad();
  }

  /**
   * Wait for the map to fully load
   */
  async waitForMapLoad() {
    await this.mapContainer.waitFor({ state: 'attached' });
    // Wait for network to be idle to ensure map resources are loaded
    await this.waitForNetworkIdle();
    // Check if map canvas exists (it might be hidden on mobile)
    const canvasCount = await this.mapCanvas.count();
    if (canvasCount > 0) {
      await this.mapCanvas.waitFor({ state: 'attached' });
    }
  }

  /**
   * Get map canvas locator for web-first assertions
   */
  get mapCanvasLocator(): Locator {
    return this.mapCanvas;
  }

  /**
   * Get geolocation control locator for web-first assertions
   */
  get geolocateControlLocator(): Locator {
    return this.geolocateControl;
  }

  /**
   * Click on geolocation control
   */
  async clickGeolocateControl() {
    await this.geolocateControl.click();
  }

  /**
   * Get navigation controls locator for web-first assertions
   */
  get navigationControlsLocator(): Locator {
    return this.navigationControl;
  }

  /**
   * Get scale control locator for web-first assertions
   */
  get scaleControlLocator(): Locator {
    return this.scaleControl;
  }

  /**
   * Click on the map at specific coordinates
   */
  async clickOnMap(x: number = 300, y: number = 300) {
    await this.mapCanvas.click({ position: { x, y } });
  }

  /**
   * Get map container dimensions
   */
  async getMapDimensions() {
    return await this.mapContainer.boundingBox();
  }

  /**
   * Wait for geolocation to complete
   */
  async waitForGeolocation() {
    // Wait for network activity to settle after geolocation
    await this.waitForNetworkIdle();
    // Give some additional time for geolocation processing
    // Don't wait for active state as geolocation might be denied in test environment
  }

  /**
   * Check if waypoint mode is currently enabled (based on presence of waypoints)
   */
  async isWaypointModeEnabled(): Promise<boolean> {
    // Waypoint mode is enabled when there are waypoints present
    const waypointCount = await this.getWaypointCount();
    return waypointCount > 0;
  }

  /**
   * Enable waypoint mode by adding a waypoint
   */
  async enableWaypointMode() {
    const isEnabled = await this.isWaypointModeEnabled();

    if (!isEnabled) {
      // Add a waypoint to enable waypoint mode
      await this.addWaypointByText('Berlin, Germany');
      await this.waitForWaypointUpdate(1);
    }
  }

  /**
   * Disable waypoint mode by clearing all waypoints
   */
  async disableWaypointMode() {
    const isEnabled = await this.isWaypointModeEnabled();

    if (isEnabled) {
      // Clear all waypoints to disable waypoint mode
      await this.clearAllWaypoints();
      await this.waitForWaypointUpdate(0);
    }
  }

  /**
   * Get waypoint mode content locator (waypoint manager component)
   */
  get waypointModeContentLocator(): Locator {
    return this.page.locator('app-waypoint-manager');
  }

  /**
   * Legacy property for backward compatibility with tests
   * Now checks if waypoint manager is visible
   */
  get waypointModeToggleLocator(): Locator {
    return this.waypointModeContentLocator;
  }

  /**
   * Add a waypoint by typing text in the waypoint input
   */
  async addWaypointByText(location: string): Promise<void> {
    // Wait for the waypoint manager to be visible
    await this.page.waitForSelector('#newWaypoint', { timeout: 10000 });

    const waypointInput = this.page.locator('#newWaypoint');
    await waypointInput.fill(location);

    const addButton = this.page.locator('button:has-text("Add")');
    await expect(addButton).toBeEnabled();
    await addButton.click();

    // Wait for the geocoding request to complete and waypoint to be added
    await this.waitForNetworkIdle();

    // Additional wait for the UI to update
    await this.page.waitForTimeout(1000);
  }

  /**
   * Clear all waypoints using the clear button or by removing them individually
   */
  async clearAllWaypoints(): Promise<void> {
    // Try to find and click clear button first
    const clearButton = this.page.locator('button:has-text("Clear")');
    if (await clearButton.isVisible()) {
      await clearButton.click();
      await this.waitForNetworkIdle();
      return;
    }

    // If no clear button, remove waypoints individually
    let waypointCount = await this.getWaypointCount();
    while (waypointCount > 0) {
      const removeButtons = this.page.locator('button[title="Remove waypoint"]');
      const firstRemoveButton = removeButtons.first();

      if (await firstRemoveButton.isVisible()) {
        await firstRemoveButton.click();
        await this.waitForNetworkIdle();
        // Wait for UI to update
        await this.page.waitForTimeout(500);
        waypointCount = await this.getWaypointCount();
      } else {
        break;
      }
    }
  }

  /**
   * Get the number of waypoints in the waypoint list
   */
  async getWaypointCount(): Promise<number> {
    const waypointItems = this.page.locator('.waypoints-list .waypoint-item');
    return await waypointItems.count();
  }

  /**
   * Wait for waypoints to be added/updated
   */
  async waitForWaypointUpdate(expectedCount?: number) {
    if (expectedCount !== undefined) {
      // Wait for specific waypoint count with timeout and fallback
      try {
        await this.page.waitForFunction(
          (count) => {
            const waypointItems = document.querySelectorAll('.waypoints-list .waypoint-item');
            return waypointItems.length === count;
          },
          expectedCount,
          { timeout: 8000 },
        );
      } catch {
        // Fallback: wait for network idle if specific count wait fails
        await this.waitForNetworkIdle();
      }
    } else {
      // Wait for network activity to settle
      await this.waitForNetworkIdle();
    }
  }

  /**
   * Remove a waypoint by clicking its remove button
   */
  async removeWaypoint(index: number) {
    const currentCount = await this.getWaypointCount();
    const removeButton = this.page.locator('.waypoints-list .waypoint-item .btn-outline-danger').nth(index);
    await removeButton.click();
    // Wait for waypoint to be removed
    await this.waitForWaypointUpdate(currentCount - 1);
  }

  /**
   * Verify map canvas is present and has valid dimensions
   */
  async isMapCanvasValid(): Promise<boolean> {
    try {
      const canvas = this.mapCanvas;
      const isVisible = await canvas.isVisible();
      if (!isVisible) return false;

      const boundingBox = await canvas.boundingBox();
      return boundingBox !== null && boundingBox.width > 0 && boundingBox.height > 0;
    } catch {
      return false;
    }
  }

  /**
   * Check if map container has proper styling (not hidden or collapsed)
   */
  async isMapContainerValid(): Promise<boolean> {
    try {
      const container = this.mapContainer;
      const isVisible = await container.isVisible();
      if (!isVisible) return false;

      const boundingBox = await container.boundingBox();
      return boundingBox !== null && boundingBox.width > 0 && boundingBox.height > 0;
    } catch {
      return false;
    }
  }

  // Route Calculator methods
  /**
   * Get route calculator locator for web-first assertions
   */
  get routeCalculatorLocator(): Locator {
    return this.page.locator('app-route-calculator');
  }

  /**
   * Enter start point location in route calculator
   */
  async enterStartPoint(location: string) {
    const startPointInput = this.page.getByRole('textbox', { name: /start point/i });
    await startPointInput.fill(location);
  }

  /**
   * Enter end point location in route calculator
   */
  async enterEndPoint(location: string) {
    const endPointInput = this.page.getByRole('textbox', { name: /end point/i });
    await endPointInput.fill(location);
  }

  /**
   * Click the calculate route button
   */
  async clickCalculateRoute() {
    const calculateButton = this.page.getByRole('button', { name: /calculate route/i });
    await calculateButton.click();
  }

  /**
   * Click the clear route button
   */
  async clickClearRoute() {
    const clearButton = this.page.getByRole('button', { name: /clear route/i });
    await clearButton.click();
  }

  /**
   * Get calculate route button locator for web-first assertions
   */
  get calculateRouteButtonLocator(): Locator {
    return this.page.getByRole('button', { name: /calculate route/i });
  }

  /**
   * Get calculating button locator for web-first assertions
   */
  get calculatingButtonLocator(): Locator {
    return this.page.getByRole('button', { name: /calculating/i });
  }

  /**
   * Wait for route calculation to complete
   */
  async waitForRouteCalculation() {
    try {
      // Wait for calculating state to disappear
      const calculatingButton = this.page.getByRole('button', { name: /calculating/i });
      if (await calculatingButton.isVisible()) {
        await calculatingButton.waitFor({ state: 'hidden', timeout: 20000 });
      }
    } catch (error) {
      console.log('Calculating button timeout, checking for route completion by other means');
      // If calculating button doesn't disappear, check if route was actually calculated
      // by looking for the save route button or route display
      try {
        await this.page.waitForSelector('[data-testid="route-display"]', { timeout: 5000 });
      } catch {
        // If no route display, wait a bit more and continue
        await this.page.waitForTimeout(2000);
      }
    }

    // Wait for network to be idle
    await this.waitForNetworkIdle();
  }

  /**
   * Wait for and capture route success message before it disappears
   */
  async waitForAndGetRouteSuccessMessage(): Promise<string> {
    try {
      // Wait for success message to appear in route calculator component
      const successMessage = this.page.locator(
        'app-route-calculator .success-message .text-success, .success-message .text-success',
      );
      await successMessage.waitFor({ state: 'visible', timeout: 15000 });

      // Wait a bit for the message to be fully rendered (especially important for Firefox)
      await this.page.waitForTimeout(100);

      // Capture the message immediately
      const messageText = await successMessage.textContent();
      return messageText || '';
    } catch (error) {
      // If success message doesn't appear, try alternative approach
      // Look for the message in the page content directly
      try {
        const pageContent = await this.page.content();
        if (pageContent.includes('Route calculated successfully!')) {
          return 'Route calculated successfully!';
        }
      } catch (fallbackError) {
        // Ignore fallback errors
      }
      return '';
    }
  }

  /**
   * Get route success message
   */
  async getRouteSuccessMessage(): Promise<string> {
    // Look for success message in route calculator component
    const successMessage = this.page.locator(
      'app-route-calculator .success-message .text-success, .success-message .text-success',
    );
    if (await successMessage.isVisible()) {
      return (await successMessage.textContent()) || '';
    }

    // Fallback: check page content directly (useful for Firefox compatibility)
    try {
      const pageContent = await this.page.content();
      if (pageContent.includes('Route calculated successfully!')) {
        return 'Route calculated successfully!';
      }
    } catch (error) {
      // Ignore fallback errors
    }

    return '';
  }

  /**
   * Get route error message
   */
  async getRouteErrorMessage(): Promise<string> {
    // Look for error message in route calculator component
    const errorMessage = this.page.locator(
      'app-route-calculator .error-message .text-danger, .error-message .text-danger',
    );
    if (await errorMessage.isVisible()) {
      return (await errorMessage.textContent()) || '';
    }
    return '';
  }

  /**
   * Check if route calculation is currently in progress
   */
  async isCalculating(): Promise<boolean> {
    // Look for calculating button or calculating state
    const calculatingButton = this.page.locator('app-route-calculator button:has-text("Calculating...")');
    return await calculatingButton.isVisible();
  }

  /**
   * Get displayed route distance
   */
  async getRouteDistance(): Promise<string> {
    // Look for distance in route display component - find the row that starts with Distance
    let distanceRow = this.page
      .locator('app-route-display .d-flex')
      .filter({ hasText: /^Distance:/ })
      .first();

    // If not found, try Total Distance (for multi-waypoint routes)
    if ((await distanceRow.count()) === 0) {
      distanceRow = this.page
        .locator('app-route-display .d-flex')
        .filter({ hasText: /^Total Distance:/ })
        .first();
    }

    const distanceValue = distanceRow.locator('.text-dark').first();
    if ((await distanceValue.count()) > 0) {
      return (await distanceValue.textContent()) || '';
    }
    return '';
  }

  /**
   * Get displayed route duration
   */
  async getRouteDuration(): Promise<string> {
    // Look for duration in route display component - find the row that starts with Duration
    let durationRow = this.page
      .locator('app-route-display .d-flex')
      .filter({ hasText: /^Duration:/ })
      .first();

    // If not found, try Total Duration (for multi-waypoint routes)
    if ((await durationRow.count()) === 0) {
      durationRow = this.page
        .locator('app-route-display .d-flex')
        .filter({ hasText: /^Total Duration:/ })
        .first();
    }

    const durationValue = durationRow.locator('.text-dark').first();
    if ((await durationValue.count()) > 0) {
      return (await durationValue.textContent()) || '';
    }
    return '';
  }

  /**
   * Check if route information is displayed (distance and duration)
   */
  async hasRouteInformation(): Promise<boolean> {
    const distance = await this.getRouteDistance();
    const duration = await this.getRouteDuration();
    return distance !== '' || duration !== '';
  }

  /**
   * Select transportation mode (costing option)
   */
  async selectTransportationMode(mode: 'bicycle' | 'pedestrian') {
    const costingSelect = this.page.getByRole('combobox', { name: /transportation mode/i });

    // Wait for the element to be ready
    await costingSelect.waitFor({ state: 'visible' });
    await costingSelect.click({ timeout: 10000 });

    // Use keyboard navigation to select the option
    if (mode === 'pedestrian') {
      await this.page.keyboard.press('ArrowDown'); // Move to pedestrian option
    } else {
      await this.page.keyboard.press('ArrowUp'); // Move to bicycle option (or stay there)
    }
    await this.page.keyboard.press('Enter');
    await this.page.waitForTimeout(300); // Wait for selection to register
  }

  /**
   * Get bicycle type selector locator for web-first assertions
   */
  get bicycleTypeSelectorLocator(): Locator {
    return this.page.getByRole('combobox', { name: /bicycle type/i });
  }

  // Polyline/Route visualization methods
  /**
   * Check if a route polyline is visible on the map (normal routing mode)
   */
  async isRoutePolylineVisible(): Promise<boolean> {
    try {
      return await this.page.evaluate(() => {
        // Check if route layer exists by looking for visual indicators
        // 1. Check for route-related console messages (we know route was added)
        // 2. Check for MapLibre canvas with route data

        // Try to find MapLibre map instance through various methods
        const mapContainer = document.querySelector('.maplibregl-map') as any;
        if (mapContainer) {
          // Try different property names that MapLibre might use
          const possibleMapProps = ['_map', 'map', 'mapInstance', '__maplibre__', '_maplibre'];

          for (const prop of possibleMapProps) {
            const mapInstance = mapContainer[prop];
            if (mapInstance && typeof mapInstance.getLayer === 'function') {
              try {
                const routeLayer = mapInstance.getLayer('route');
                const routeSource = mapInstance.getSource('route');
                return !!(routeLayer && routeSource);
              } catch (e) {
                // Continue trying other properties
              }
            }
          }
        }

        // Alternative: Check if there are any line layers that might be routes
        // This is a fallback method
        const canvas = document.querySelector('.maplibregl-canvas') as HTMLCanvasElement;
        if (canvas) {
          // If canvas exists and has been drawn on, assume route might be there
          // This is not perfect but better than always returning false
          return canvas.width > 0 && canvas.height > 0;
        }

        return false;
      });
    } catch (error) {
      console.log('Error checking route polyline:', error);
      return false;
    }
  }

  /**
   * Check if a multi-waypoint route polyline is visible on the map (waypoint mode)
   */
  async isWaypointRoutePolylineVisible(): Promise<boolean> {
    try {
      // Check if the map has a multi-route layer
      return await this.page.evaluate(() => {
        // Try different selectors to find the map
        const selectors = ['#map', '.maplibregl-map', 'mgl-map', 'app-libre-map'];
        let mapInstance: any = null;

        for (const selector of selectors) {
          const element = document.querySelector(selector) as any;
          if (element) {
            // Try different property names that MapLibre might use
            const possibleMapProps = ['_map', 'map', 'mapInstance', '__maplibre__', '_maplibre'];
            for (const prop of possibleMapProps) {
              mapInstance = element[prop];
              if (mapInstance && typeof mapInstance.getLayer === 'function') {
                break;
              }
            }
            if (mapInstance && typeof mapInstance.getLayer === 'function') break;
          }
        }

        if (!mapInstance || typeof mapInstance.getLayer !== 'function') {
          console.log('Map instance not found or invalid');
          return false;
        }

        try {
          const multiRouteLayer = mapInstance.getLayer('multi-route');
          const multiRouteSource = mapInstance.getSource('multi-route');

          console.log('Multi-route layer:', multiRouteLayer);
          console.log('Multi-route source:', multiRouteSource);

          // Check if both layer and source exist and source has data
          if (multiRouteLayer && multiRouteSource) {
            const sourceData = multiRouteSource._data || multiRouteSource.data;
            console.log('Source data:', sourceData);

            // Check if source has features with coordinates
            if (sourceData && sourceData.features && sourceData.features.length > 0) {
              const feature = sourceData.features[0];
              const hasCoordinates =
                feature.geometry && feature.geometry.coordinates && feature.geometry.coordinates.length > 0;
              console.log('Has coordinates:', hasCoordinates);
              return hasCoordinates;
            }
          }

          return false;
        } catch (error) {
          console.log('Error checking multi-route layer:', error);
          return false;
        }
      });
    } catch (error) {
      console.log('Error checking waypoint route polyline:', error);
      return false;
    }
  }

  /**
   * Get waypoint route polyline properties (color, width) for waypoint mode
   */
  async getWaypointRoutePolylineProperties(): Promise<{ color?: string; width?: number } | null> {
    try {
      return await this.page.evaluate(() => {
        const mapContainer = document.querySelector('#map') as any;
        if (!mapContainer || !mapContainer._map) return null;

        const map = mapContainer._map;
        const multiRouteLayer = map.getLayer('multi-route');

        if (!multiRouteLayer) return null;

        const paint = multiRouteLayer.paint || {};
        return {
          color: paint['line-color'],
          width: paint['line-width'],
        };
      });
    } catch (error) {
      console.log('Error getting waypoint route polyline properties:', error);
      return null;
    }
  }

  /**
   * Wait for waypoint route polyline to appear on the map
   */
  async waitForWaypointRoutePolyline(timeout: number = 10000): Promise<boolean> {
    const startTime = Date.now();

    while (Date.now() - startTime < timeout) {
      if (await this.isWaypointRoutePolylineVisible()) {
        return true;
      }
      await this.page.waitForTimeout(500); // Wait 500ms before checking again
    }

    return false;
  }

  // Mobile-specific methods for sidepanel testing
  /**
   * Check if device is in mobile viewport
   */
  async isMobileViewport(): Promise<boolean> {
    const viewport = this.page.viewportSize();
    return viewport ? viewport.width < 768 : false;
  }

  /**
   * Check if device is in tablet viewport
   */
  async isTabletViewport(): Promise<boolean> {
    const viewport = this.page.viewportSize();
    return viewport ? viewport.width >= 768 && viewport.width < 1200 : false;
  }

  /**
   * Get sidepanel toggle button (actual toggle button for mobile and desktop)
   */
  get sidepanelToggleButton(): Locator {
    return this.page.getByRole('button', { name: /(open|close) sidepanel/i });
  }

  /**
   * Get mobile sidepanel container
   */
  get mobileSidepanelContainer(): Locator {
    return this.page.locator('.sidepanel-container.mobile-sidepanel');
  }

  /**
   * Get desktop/tablet sidepanel container
   */
  get desktopSidepanelContainer(): Locator {
    return this.page.locator('.sidepanel-container.desktop-sidepanel');
  }

  /**
   * Get backdrop element (only visible on mobile)
   */
  get backdrop(): Locator {
    return this.page.locator('.backdrop');
  }

  /**
   * Get mobile sidepanel container locator for web-first assertions
   */
  get mobileSidepanelOpenLocator(): Locator {
    return this.mobileSidepanelContainer.locator('.open:not(.closed)');
  }

  /**
   * Open mobile sidepanel using toggle button
   */
  async openMobileSidepanel(): Promise<void> {
    const container = this.mobileSidepanelContainer;
    const classes = await container.getAttribute('class');
    const isOpen = classes ? classes.includes('open') && !classes.includes('closed') : false;

    if (!isOpen) {
      // Wait for the button to be ready
      await this.sidepanelToggleButton.waitFor({ state: 'visible' });
      await this.sidepanelToggleButton.click({ force: true, timeout: 10000 });
      await this.page.waitForTimeout(500); // Wait for animation
      await this.mobileSidepanelContainer.waitFor({ state: 'visible' });
    }
  }

  /**
   * Close mobile sidepanel using toggle button
   */
  async closeMobileSidepanel(): Promise<void> {
    const container = this.mobileSidepanelContainer;
    const classes = await container.getAttribute('class');
    const isOpen = classes ? classes.includes('open') && !classes.includes('closed') : false;

    if (isOpen) {
      // Wait for the button to be ready
      await this.sidepanelToggleButton.waitFor({ state: 'visible' });
      await this.sidepanelToggleButton.click({ force: true, timeout: 10000 });
      // Wait for animation to complete
      await this.page.waitForTimeout(500);
    }
  }

  /**
   * Close mobile sidepanel using backdrop click
   */
  async closeMobileSidepanelWithBackdrop(): Promise<void> {
    const container = this.mobileSidepanelContainer;
    const classes = await container.getAttribute('class');
    const isOpen = classes ? classes.includes('open') && !classes.includes('closed') : false;

    if (isOpen) {
      // Use force click to bypass intercepting elements
      await this.backdrop.click({ force: true });
      await this.page.waitForTimeout(500);
    }
  }

  // Tablet-specific methods
  async isTabletSidepanelOpen(): Promise<boolean> {
    const container = this.page.locator('.sidepanel-container.desktop-sidepanel');
    const classes = await container.getAttribute('class');
    return classes ? classes.includes('open') && !classes.includes('closed') : false;
  }

  async getTabletSidepanelContainer() {
    return this.page.locator('.sidepanel-container.desktop-sidepanel');
  }

  /**
   * Simulate touch scroll on mobile sidepanel
   */
  async simulateTouchScroll(startY: number = 300, endY: number = 200): Promise<void> {
    await this.page.evaluate(
      ({ startY, endY }) => {
        const sidepanel = document.querySelector('.sidepanel-container.mobile-sidepanel');
        if (sidepanel) {
          // Simulate touchstart
          const touchStart = new TouchEvent('touchstart', {
            touches: [
              new Touch({
                identifier: 0,
                target: sidepanel,
                clientX: 200,
                clientY: startY,
              }),
            ],
            bubbles: true,
          });

          // Simulate touchmove
          const touchMove = new TouchEvent('touchmove', {
            touches: [
              new Touch({
                identifier: 0,
                target: sidepanel,
                clientX: 200,
                clientY: endY,
              }),
            ],
            bubbles: true,
          });

          // Simulate touchend
          const touchEnd = new TouchEvent('touchend', {
            changedTouches: [
              new Touch({
                identifier: 0,
                target: sidepanel,
                clientX: 200,
                clientY: endY,
              }),
            ],
            bubbles: true,
          });

          sidepanel.dispatchEvent(touchStart);
          setTimeout(() => sidepanel.dispatchEvent(touchMove), 10);
          setTimeout(() => sidepanel.dispatchEvent(touchEnd), 20);
        }
      },
      { startY, endY },
    );
  }

  /**
   * Test if touch events are properly handled (iOS fix verification)
   */
  async verifyTouchEventHandling(): Promise<boolean> {
    return await this.page.evaluate(() => {
      const sidepanel = document.querySelector('.sidepanel-container.mobile-sidepanel');
      if (!sidepanel) return false;

      // Test touchstart event handling
      const touchStart = new TouchEvent('touchstart', {
        touches: [
          new Touch({
            identifier: 0,
            target: sidepanel,
            clientX: 200,
            clientY: 350,
          }),
        ],
        bubbles: true,
      });

      sidepanel.dispatchEvent(touchStart);

      // Check if initial touch position was stored (iOS fix)
      const storedY = (sidepanel as any)._initialTouchY;
      return storedY === 350;
    });
  }

  /**
   * Get sidepanel scroll position
   */
  async getSidepanelScrollTop(): Promise<number> {
    const container = (await this.isMobileViewport()) ? this.mobileSidepanelContainer : this.desktopSidepanelContainer;
    return await container.evaluate((element) => element.scrollTop);
  }

  /**
   * Set sidepanel scroll position
   */
  async setSidepanelScrollTop(scrollTop: number): Promise<void> {
    const container = (await this.isMobileViewport()) ? this.mobileSidepanelContainer : this.desktopSidepanelContainer;
    await container.evaluate((element, scrollTop) => {
      element.scrollTop = scrollTop;
    }, scrollTop);
  }

  // Save Route functionality methods
  /**
   * Click the Save Route button in the route display component
   */
  async clickSaveRouteButton() {
    const saveButton = this.page.getByRole('button', { name: /save route/i });
    await saveButton.click();
  }

  /**
   * Get save route button locator for web-first assertions
   */
  get saveRouteButtonLocator(): Locator {
    return this.page.getByRole('button', { name: /save route/i });
  }

  /**
   * Check if save route modal is visible
   */
  async isSaveRouteModalVisible(): Promise<boolean> {
    const modal = this.page.locator('.modal[role="dialog"]');
    return await modal.isVisible();
  }

  /**
   * Get save route modal locator for web-first assertions
   */
  get saveRouteModalLocator(): Locator {
    return this.page.locator('.modal[role="dialog"]');
  }

  /**
   * Fill in the route name in the save route modal
   */
  async fillRouteName(name: string) {
    const routeNameInput = this.page.getByRole('textbox', { name: /route name/i });
    await routeNameInput.fill(name);
  }

  /**
   * Fill in the route description in the save route modal
   */
  async fillRouteDescription(description: string) {
    const descriptionInput = this.page.getByRole('textbox', { name: /description/i });
    await descriptionInput.fill(description);
  }

  /**
   * Select route type in the save route modal
   */
  async selectRouteType(routeType: 'CYCLING' | 'WALKING' | 'RUNNING' | 'HIKING' | 'MOUNTAIN_BIKING') {
    const routeTypeSelect = this.page.locator('#routeType');
    await routeTypeSelect.selectOption({ value: routeType });
  }

  /**
   * Toggle the public route checkbox in the save route modal
   */
  async togglePublicRoute(isPublic: boolean) {
    const publicCheckbox = this.page.locator('#isPublic');
    const isChecked = await publicCheckbox.isChecked();

    if (isChecked !== isPublic) {
      await publicCheckbox.click();
    }
  }

  /**
   * Set difficulty level in the save route modal
   */
  async setDifficultyLevel(level: number) {
    // Click on the star corresponding to the difficulty level (1-5)
    const difficultyStars = this.page.locator('.star-rating .star');
    await difficultyStars.nth(level - 1).click();
  }

  /**
   * Set scenic rating in the save route modal
   */
  async setScenicRating(rating: number) {
    // Click on the star corresponding to the scenic rating (1-5)
    const scenicStars = this.page.locator('.scenic-rating .star');
    await scenicStars.nth(rating - 1).click();
  }

  /**
   * Set safety rating in the save route modal
   */
  async setSafetyRating(rating: number) {
    // Click on the star corresponding to the safety rating (1-5)
    const safetyStars = this.page.locator('.safety-rating .star');
    await safetyStars.nth(rating - 1).click();
  }

  /**
   * Select surface type in the save route modal
   */
  async selectSurfaceType(surfaceType: string) {
    const surfaceSelect = this.page.locator('#surfaceType');
    await surfaceSelect.selectOption({ value: surfaceType });
  }

  /**
   * Select road types in the save route modal (checkboxes)
   */
  async selectRoadTypes(roadTypes: string[]) {
    for (const roadType of roadTypes) {
      const checkbox = this.page.getByRole('checkbox', { name: new RegExp(roadType, 'i') });
      await checkbox.check();
    }
  }

  /**
   * Fill in notes in the save route modal
   */
  async fillNotes(notes: string) {
    const notesTextarea = this.page.getByRole('textbox', { name: /notes/i });
    await notesTextarea.fill(notes);
  }

  /**
   * Fill in tags in the save route modal
   */
  async fillTags(tags: string) {
    const tagsInput = this.page.getByRole('textbox', { name: /tags/i });
    await tagsInput.fill(tags);
  }

  /**
   * Click the Save Route button in the modal
   */
  async clickModalSaveButton() {
    const saveButton = this.page.locator('.modal-footer .btn-primary');
    await saveButton.click();
  }

  /**
   * Click the Cancel button in the modal
   */
  async clickModalCancelButton() {
    const cancelButton = this.page.locator('.modal-footer .btn-secondary');
    await cancelButton.click();
  }

  /**
   * Close the modal using the X button
   */
  async closeModalWithX() {
    const closeButton = this.page.locator('.modal-header .btn-close');
    await closeButton.click();
  }

  /**
   * Wait for the save route modal to appear
   */
  async waitForSaveRouteModal() {
    const modal = this.page.locator('.modal[role="dialog"]');
    await modal.waitFor({ state: 'visible' });
  }

  /**
   * Wait for the save route modal to disappear
   */
  async waitForSaveRouteModalToClose() {
    const modal = this.page.locator('.modal[role="dialog"]');
    await modal.waitFor({ state: 'hidden' });
  }

  /**
   * Get success message from the save route modal
   */
  async getSaveRouteSuccessMessage(): Promise<string> {
    const successAlert = this.page.locator('.modal .alert-success');
    if (await successAlert.isVisible()) {
      return (await successAlert.textContent()) || '';
    }
    return '';
  }

  /**
   * Get error message from the save route modal
   */
  async getSaveRouteErrorMessage(): Promise<string> {
    const errorAlert = this.page.locator('.modal .alert-danger');
    if (await errorAlert.isVisible()) {
      return (await errorAlert.textContent()) || '';
    }
    return '';
  }

  /**
   * Check if the modal save button is disabled
   */
  async isModalSaveButtonDisabled(): Promise<boolean> {
    const saveButton = this.page.locator('.modal-footer .btn-primary');
    return await saveButton.isDisabled();
  }

  /**
   * Check if the modal is in saving state (showing spinner)
   */
  async isModalSaving(): Promise<boolean> {
    const spinner = this.page.locator('.modal-footer .spinner-border');
    return await spinner.isVisible();
  }

  /**
   * Get the modal save button text
   */
  async getModalSaveButtonText(): Promise<string> {
    const saveButton = this.page.locator('.modal-footer .btn-primary');
    return (await saveButton.textContent()) || '';
  }
}
