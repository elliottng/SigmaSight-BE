import { z } from "zod";
// Backend API response schemas based on SigmaSight backend models
export const PortfolioSnapshot = z.object({
    id: z.string(),
    portfolio_id: z.string(),
    as_of: z.string(),
    total_value: z.number(),
    cash: z.number(),
    equity_value: z.number(),
    gross_exposure: z.number(),
    net_exposure: z.number(),
    long_exposure: z.number(),
    short_exposure: z.number(),
    gross_exposure_pct: z.number(),
    net_exposure_pct: z.number(),
    long_exposure_pct: z.number(),
    short_exposure_pct: z.number(),
});
export const Position = z.object({
    id: z.string(),
    portfolio_id: z.string(),
    symbol: z.string(),
    side: z.enum(["LONG", "SHORT"]),
    quantity: z.number(),
    avg_cost: z.number(),
    market_price: z.number(),
    market_value: z.number(),
    unrealized_pnl: z.number(),
    unrealized_pnl_pct: z.number(),
    sector: z.string().nullable(),
    industry: z.string().nullable(),
    as_of: z.string(),
});
export const PositionFactorExposure = z.object({
    id: z.string(),
    position_id: z.string(),
    factor_id: z.string(),
    factor_name: z.string(),
    beta: z.number(),
    as_of: z.string(),
});
export const RiskMetrics = z.object({
    portfolio_id: z.string(),
    as_of: z.string(),
    var_1d_95: z.number().nullable(),
    var_1d_99: z.number().nullable(),
    var_10d_95: z.number().nullable(),
    var_10d_99: z.number().nullable(),
    es_1d_95: z.number().nullable(),
    es_1d_99: z.number().nullable(),
    es_10d_95: z.number().nullable(),
    es_10d_99: z.number().nullable(),
});
export const StressTestResult = z.object({
    scenario_name: z.string(),
    portfolio_id: z.string(),
    pnl_amount: z.number(),
    pnl_pct: z.number(),
    as_of: z.string(),
});
export class BackendClient {
    baseUrl;
    authToken;
    constructor(baseUrl = "http://localhost:8000", authToken) {
        this.baseUrl = baseUrl.replace(/\/$/, ""); // Remove trailing slash
        this.authToken = authToken;
    }
    async request(endpoint, options) {
        const url = `${this.baseUrl}${endpoint}`;
        const headers = {
            "Content-Type": "application/json",
            ...options?.headers,
        };
        if (this.authToken) {
            headers["Authorization"] = `Bearer ${this.authToken}`;
        }
        try {
            const response = await fetch(url, {
                ...options,
                headers,
            });
            if (!response.ok) {
                throw new Error(`Backend API error: ${response.status} ${response.statusText}`);
            }
            return await response.json();
        }
        catch (error) {
            console.error(`Backend API request failed: ${endpoint}`, error);
            throw new Error(`Backend API unavailable: ${error instanceof Error ? error.message : 'Unknown error'}`);
        }
    }
    async getPortfolioSnapshot(portfolioId, asOf) {
        try {
            // For now, use the reports API to get portfolio data
            // This will be updated when the full portfolio API is implemented
            const reportContent = await this.getPortfolioReport(portfolioId, "json");
            if (reportContent && reportContent.portfolio_snapshot) {
                return PortfolioSnapshot.parse(reportContent.portfolio_snapshot);
            }
            return null;
        }
        catch (error) {
            console.error("Failed to get portfolio snapshot:", error);
            return null;
        }
    }
    async getPortfolioReport(portfolioId, format = "json") {
        try {
            const endpoint = `/api/v1/reports/portfolio/${portfolioId}/content/${format}`;
            const response = await this.request(endpoint);
            return response;
        }
        catch (error) {
            console.error("Failed to get portfolio report:", error);
            return null;
        }
    }
    async getPositions(portfolioId, asOf) {
        try {
            // For now, use the reports API to get portfolio data
            const reportContent = await this.getPortfolioReport(portfolioId, "json");
            if (reportContent && reportContent.positions) {
                // Convert report positions to our Position schema
                return reportContent.positions.map((pos) => Position.parse({
                    id: pos.id || `${portfolioId}-${pos.symbol}`,
                    portfolio_id: portfolioId,
                    symbol: pos.symbol,
                    side: pos.side || (pos.quantity > 0 ? "LONG" : "SHORT"),
                    quantity: pos.quantity,
                    avg_cost: pos.avg_cost || pos.cost_basis,
                    market_price: pos.market_price || pos.current_price,
                    market_value: pos.market_value,
                    unrealized_pnl: pos.unrealized_pnl || 0,
                    unrealized_pnl_pct: pos.unrealized_pnl_pct || 0,
                    sector: pos.sector,
                    industry: pos.industry,
                    as_of: reportContent.as_of || new Date().toISOString().split('T')[0]
                }));
            }
            return [];
        }
        catch (error) {
            console.error("Failed to get positions:", error);
            return [];
        }
    }
    async getFactorExposures(portfolioId, asOf) {
        try {
            const params = new URLSearchParams();
            if (asOf)
                params.set("as_of", asOf);
            const endpoint = `/api/v1/portfolio/${portfolioId}/factors${params.toString() ? `?${params}` : ""}`;
            const response = await this.request(endpoint);
            return z.array(PositionFactorExposure).parse(response);
        }
        catch (error) {
            console.error("Failed to get factor exposures:", error);
            return [];
        }
    }
    async getRiskMetrics(portfolioId, asOf) {
        try {
            const params = new URLSearchParams();
            if (asOf)
                params.set("as_of", asOf);
            const endpoint = `/api/v1/portfolio/${portfolioId}/risk${params.toString() ? `?${params}` : ""}`;
            const response = await this.request(endpoint);
            return RiskMetrics.parse(response);
        }
        catch (error) {
            console.error("Failed to get risk metrics:", error);
            return null;
        }
    }
    async runStressTest(portfolioId, scenarios) {
        try {
            const endpoint = `/api/v1/portfolio/${portfolioId}/stress-test`;
            const response = await this.request(endpoint, {
                method: "POST",
                body: JSON.stringify({ scenarios }),
            });
            return z.array(StressTestResult).parse(response);
        }
        catch (error) {
            console.error("Failed to run stress test:", error);
            return [];
        }
    }
    // Health check to verify backend connectivity
    async healthCheck() {
        try {
            await this.request("/health");
            return true;
        }
        catch {
            return false;
        }
    }
}
