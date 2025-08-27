'use client'

import { useState, useEffect } from 'react'
import ProtectedRoute from '../../components/auth/ProtectedRoute'
import DashboardLayout from '../../components/layout/DashboardLayout'
import { Card, CardContent, CardHeader, CardTitle } from '../../components/ui/Card'
import { Button } from '../../components/ui/Button'
import { reportsApi } from '../../services/api'
import { 
  FileText, 
  Download, 
  Eye, 
  Calendar,
  Clock,
  Settings,
  Plus,
  Filter,
  RefreshCcw,
  Mail,
  Share2
} from 'lucide-react'
import { formatDateTime } from '../../lib/utils'
import type { ReportTemplate } from '../../lib/types'

interface GeneratedReport {
  id: string
  name: string
  type: string
  format: 'pdf' | 'json' | 'csv'
  generated_at: string
  size: number
  download_url: string
  status: 'completed' | 'generating' | 'failed'
}

export default function ReportsPage() {
  const [templates, setTemplates] = useState<ReportTemplate[]>([])
  const [reports, setReports] = useState<GeneratedReport[]>([])
  const [loading, setLoading] = useState(true)
  const [generating, setGenerating] = useState<string | null>(null)
  const [activeTab, setActiveTab] = useState<'generate' | 'history'>('generate')

  useEffect(() => {
    const fetchData = async () => {
      try {
        const templatesData = await reportsApi.getReportTemplates()
        setTemplates(templatesData)
        
        // Mock report history for now
        setReports([
          {
            id: '1',
            name: 'Daily Risk Summary',
            type: 'risk_summary',
            format: 'pdf',
            generated_at: '2025-08-26T10:30:00Z',
            size: 245760,
            download_url: '#',
            status: 'completed'
          },
          {
            id: '2', 
            name: 'Portfolio Positions Export',
            type: 'positions',
            format: 'csv',
            generated_at: '2025-08-26T09:15:00Z',
            size: 15840,
            download_url: '#',
            status: 'completed'
          },
          {
            id: '3',
            name: 'Factor Analysis Report',
            type: 'factor_analysis',
            format: 'json',
            generated_at: '2025-08-26T08:45:00Z',
            size: 32768,
            download_url: '#',
            status: 'completed'
          }
        ])
      } catch (error) {
        console.error('Failed to fetch report data:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchData()
  }, [])

  const handleGenerateReport = async (template: ReportTemplate) => {
    setGenerating(template.id)
    try {
      const response = await reportsApi.generateReport({
        type: template.id,
        format: template.format,
        sections: template.sections
      })
      
      // For demo, simulate report generation
      setTimeout(() => {
        const newReport: GeneratedReport = {
          id: Date.now().toString(),
          name: template.name,
          type: template.id,
          format: template.format,
          generated_at: new Date().toISOString(),
          size: Math.floor(Math.random() * 500000) + 50000,
          download_url: '#',
          status: 'completed'
        }
        setReports(prev => [newReport, ...prev])
        setGenerating(null)
      }, 3000)
      
    } catch (error) {
      console.error('Failed to generate report:', error)
      setGenerating(null)
    }
  }

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  const getFormatIcon = (format: string) => {
    switch (format) {
      case 'pdf':
        return '📄'
      case 'csv':
        return '📊'
      case 'json':
        return '💻'
      default:
        return '📋'
    }
  }

  if (loading) {
    return (
      <ProtectedRoute>
        <DashboardLayout>
          <div className="space-y-6">
            <div className="animate-pulse space-y-4">
              <div className="h-8 bg-gray-300 rounded w-1/4"></div>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {[...Array(6)].map((_, i) => (
                  <div key={i} className="h-32 bg-gray-300 rounded"></div>
                ))}
              </div>
            </div>
          </div>
        </DashboardLayout>
      </ProtectedRoute>
    )
  }

  return (
    <ProtectedRoute>
      <DashboardLayout>
        <div className="space-y-8">
          {/* Page Header */}
          <div className="flex justify-between items-start">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Reports</h1>
              <p className="text-gray-600 mt-1">
                Generate and manage portfolio reports
              </p>
            </div>
            <div className="flex space-x-3">
              <Button variant="outline" className="flex items-center">
                <Settings className="h-4 w-4 mr-2" />
                Schedule
              </Button>
              <Button className="flex items-center">
                <Plus className="h-4 w-4 mr-2" />
                Custom Report
              </Button>
            </div>
          </div>

          {/* Tab Navigation */}
          <div className="border-b border-gray-200">
            <nav className="-mb-px flex space-x-8">
              <button
                onClick={() => setActiveTab('generate')}
                className={`py-2 px-1 border-b-2 font-medium text-sm ${
                  activeTab === 'generate'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                Generate Reports
              </button>
              <button
                onClick={() => setActiveTab('history')}
                className={`py-2 px-1 border-b-2 font-medium text-sm ${
                  activeTab === 'history'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                Report History ({reports.length})
              </button>
            </nav>
          </div>

          {/* Generate Reports Tab */}
          {activeTab === 'generate' && (
            <div className="space-y-6">
              {/* Quick Actions */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <Card className="cursor-pointer hover:shadow-md transition-shadow border-blue-200 bg-blue-50">
                  <CardContent className="pt-6">
                    <div className="flex items-center space-x-3">
                      <div className="p-2 bg-blue-100 rounded-lg">
                        <FileText className="h-6 w-6 text-blue-600" />
                      </div>
                      <div>
                        <h3 className="font-semibold text-blue-900">Daily Summary</h3>
                        <p className="text-sm text-blue-700">Quick portfolio overview</p>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                <Card className="cursor-pointer hover:shadow-md transition-shadow border-green-200 bg-green-50">
                  <CardContent className="pt-6">
                    <div className="flex items-center space-x-3">
                      <div className="p-2 bg-green-100 rounded-lg">
                        <Download className="h-6 w-6 text-green-600" />
                      </div>
                      <div>
                        <h3 className="font-semibold text-green-900">Data Export</h3>
                        <p className="text-sm text-green-700">CSV/JSON position data</p>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                <Card className="cursor-pointer hover:shadow-md transition-shadow border-purple-200 bg-purple-50">
                  <CardContent className="pt-6">
                    <div className="flex items-center space-x-3">
                      <div className="p-2 bg-purple-100 rounded-lg">
                        <Mail className="h-6 w-6 text-purple-600" />
                      </div>
                      <div>
                        <h3 className="font-semibold text-purple-900">Scheduled</h3>
                        <p className="text-sm text-purple-700">Automated reporting</p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>

              {/* Available Templates */}
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Available Report Templates</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {templates.map((template) => (
                    <Card key={template.id} className="hover:shadow-md transition-shadow">
                      <CardHeader>
                        <CardTitle className="flex items-center justify-between">
                          <div className="flex items-center space-x-2">
                            <span className="text-lg">{getFormatIcon(template.format)}</span>
                            <span>{template.name}</span>
                          </div>
                          <span className="text-xs bg-gray-100 px-2 py-1 rounded uppercase">
                            {template.format}
                          </span>
                        </CardTitle>
                      </CardHeader>
                      <CardContent>
                        <p className="text-sm text-gray-600 mb-4">
                          {template.description}
                        </p>
                        <div className="mb-4">
                          <h5 className="text-xs font-semibold text-gray-700 mb-1">Sections:</h5>
                          <div className="flex flex-wrap gap-1">
                            {template.sections.map((section, index) => (
                              <span
                                key={index}
                                className="text-xs bg-gray-100 px-2 py-1 rounded"
                              >
                                {section}
                              </span>
                            ))}
                          </div>
                        </div>
                        <Button
                          onClick={() => handleGenerateReport(template)}
                          disabled={generating === template.id}
                          className="w-full"
                        >
                          {generating === template.id ? (
                            <>
                              <RefreshCcw className="h-4 w-4 mr-2 animate-spin" />
                              Generating...
                            </>
                          ) : (
                            <>
                              <FileText className="h-4 w-4 mr-2" />
                              Generate Report
                            </>
                          )}
                        </Button>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              </div>

              {/* No Templates State */}
              {templates.length === 0 && (
                <Card>
                  <CardContent className="pt-6">
                    <div className="text-center py-8">
                      <FileText className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                      <h3 className="text-lg font-semibold text-gray-900 mb-2">
                        No Report Templates Available
                      </h3>
                      <p className="text-gray-600 mb-4">
                        Report templates will appear here once they're configured.
                      </p>
                      <Button variant="outline">
                        Contact Support
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              )}
            </div>
          )}

          {/* Report History Tab */}
          {activeTab === 'history' && (
            <div className="space-y-6">
              {/* Filters */}
              <div className="flex justify-between items-center">
                <div className="flex space-x-3">
                  <Button variant="outline" size="sm" className="flex items-center">
                    <Filter className="h-4 w-4 mr-2" />
                    Filter
                  </Button>
                  <Button variant="outline" size="sm" className="flex items-center">
                    <Calendar className="h-4 w-4 mr-2" />
                    Date Range
                  </Button>
                </div>
                <Button variant="outline" size="sm" className="flex items-center">
                  <RefreshCcw className="h-4 w-4 mr-2" />
                  Refresh
                </Button>
              </div>

              {/* Reports List */}
              <Card>
                <CardHeader>
                  <CardTitle>Generated Reports</CardTitle>
                </CardHeader>
                <CardContent>
                  {reports.length > 0 ? (
                    <div className="space-y-4">
                      {reports.map((report) => (
                        <div
                          key={report.id}
                          className="flex items-center justify-between p-4 border border-gray-200 rounded-lg hover:bg-gray-50"
                        >
                          <div className="flex items-center space-x-4">
                            <div className="text-2xl">
                              {getFormatIcon(report.format)}
                            </div>
                            <div>
                              <h4 className="font-semibold text-gray-900">
                                {report.name}
                              </h4>
                              <div className="flex items-center space-x-4 text-sm text-gray-500">
                                <span className="flex items-center">
                                  <Clock className="h-3 w-3 mr-1" />
                                  {formatDateTime(report.generated_at)}
                                </span>
                                <span>{formatFileSize(report.size)}</span>
                                <span className={`px-2 py-1 rounded-full text-xs ${
                                  report.status === 'completed' ? 'bg-green-100 text-green-800' :
                                  report.status === 'generating' ? 'bg-blue-100 text-blue-800' :
                                  'bg-red-100 text-red-800'
                                }`}>
                                  {report.status}
                                </span>
                              </div>
                            </div>
                          </div>
                          <div className="flex space-x-2">
                            <Button variant="outline" size="sm">
                              <Eye className="h-4 w-4 mr-2" />
                              Preview
                            </Button>
                            <Button variant="outline" size="sm">
                              <Download className="h-4 w-4 mr-2" />
                              Download
                            </Button>
                            <Button variant="outline" size="sm">
                              <Share2 className="h-4 w-4 mr-2" />
                              Share
                            </Button>
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="text-center py-8">
                      <FileText className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                      <h3 className="text-lg font-semibold text-gray-900 mb-2">
                        No Reports Generated Yet
                      </h3>
                      <p className="text-gray-600 mb-4">
                        Generate your first report to see it here.
                      </p>
                      <Button onClick={() => setActiveTab('generate')}>
                        Generate Report
                      </Button>
                    </div>
                  )}
                </CardContent>
              </Card>
            </div>
          )}

          {/* Report Info Footer */}
          <Card className="bg-blue-50 border-blue-200">
            <CardContent className="pt-6">
              <div className="flex items-start space-x-3">
                <FileText className="h-5 w-5 text-blue-600 mt-0.5" />
                <div>
                  <h4 className="font-semibold text-blue-900 mb-1">About SigmaSight Reports</h4>
                  <p className="text-sm text-blue-800 mb-2">
                    Professional-grade portfolio reports powered by institutional analytics.
                  </p>
                  <ul className="text-xs text-blue-700 space-y-1">
                    <li>• PDF reports for client presentations</li>
                    <li>• CSV exports for spreadsheet analysis</li>
                    <li>• JSON data for custom integrations</li>
                    <li>• Automated scheduling available</li>
                  </ul>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </DashboardLayout>
    </ProtectedRoute>
  )
}