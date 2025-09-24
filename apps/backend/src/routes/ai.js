const express = require('express');
const router = express.Router();
const AICodeAnalysisService = require('../services/aiCodeAnalysis');

const aiCodeAnalysis = new AICodeAnalysisService();

/**
 * @route POST /api/ai/analyze-code
 * @desc Analyze code for performance, quality, and best practices
 */
router.post('/analyze-code', async (req, res) => {
    try {
        const { code, context } = req.body;

        if (!code) {
            return res.status(400).json({
                success: false,
                error: 'Code is required for analysis'
            });
        }

        console.log('🔬 AI Code Analysis Request:', {
            codeLength: code.length,
            hasContext: !!context,
            timestamp: new Date().toISOString()
        });

        const result = await aiCodeAnalysis.analyzeCode(code, context);

        console.log('✅ AI Code Analysis Complete:', {
            success: result.success,
            hasAnalysis: !!result.analysis,
            hasFallback: !!result.fallback
        });

        res.json(result);
    } catch (error) {
        console.error('❌ AI Code Analysis Error:', error);
        res.status(500).json({
            success: false,
            error: 'Internal server error during code analysis',
            message: error.message
        });
    }
});

/**
 * @route POST /api/ai/optimize-code
 * @desc Generate code optimization suggestions
 */
router.post('/optimize-code', async (req, res) => {
    try {
        const { code, optimizationType = 'all' } = req.body;

        if (!code) {
            return res.status(400).json({
                success: false,
                error: 'Code is required for optimization'
            });
        }

        console.log('⚡ AI Code Optimization Request:', {
            codeLength: code.length,
            optimizationType,
            timestamp: new Date().toISOString()
        });

        const result = await aiCodeAnalysis.optimizeCode(code, optimizationType);

        console.log('✅ AI Code Optimization Complete:', {
            success: result.success,
            optimizationCount: result.optimizations?.length || 0
        });

        res.json(result);
    } catch (error) {
        console.error('❌ AI Code Optimization Error:', error);
        res.status(500).json({
            success: false,
            error: 'Internal server error during code optimization',
            message: error.message
        });
    }
});

/**
 * @route POST /api/ai/explain-code
 * @desc Explain code functionality and concepts
 */
router.post('/explain-code', async (req, res) => {
    try {
        const { code } = req.body;

        if (!code) {
            return res.status(400).json({
                success: false,
                error: 'Code is required for explanation'
            });
        }

        console.log('📚 AI Code Explanation Request:', {
            codeLength: code.length,
            timestamp: new Date().toISOString()
        });

        const result = await aiCodeAnalysis.explainCode(code);

        console.log('✅ AI Code Explanation Complete:', {
            success: result.success,
            hasExplanation: !!result.explanation
        });

        res.json(result);
    } catch (error) {
        console.error('❌ AI Code Explanation Error:', error);
        res.status(500).json({
            success: false,
            error: 'Internal server error during code explanation',
            message: error.message
        });
    }
});

/**
 * @route POST /api/ai/detect-issues
 * @desc Detect potential bugs and security issues
 */
router.post('/detect-issues', async (req, res) => {
    try {
        const { code } = req.body;

        if (!code) {
            return res.status(400).json({
                success: false,
                error: 'Code is required for issue detection'
            });
        }

        console.log('🔍 AI Issue Detection Request:', {
            codeLength: code.length,
            timestamp: new Date().toISOString()
        });

        const result = await aiCodeAnalysis.detectIssues(code);

        console.log('✅ AI Issue Detection Complete:', {
            success: result.success,
            issueCount: result.issues?.length || 0
        });

        res.json(result);
    } catch (error) {
        console.error('❌ AI Issue Detection Error:', error);
        res.status(500).json({
            success: false,
            error: 'Internal server error during issue detection',
            message: error.message
        });
    }
});

/**
 * @route POST /api/ai/generate-tests
 * @desc Generate unit tests for the code
 */
router.post('/generate-tests', async (req, res) => {
    try {
        const { code } = req.body;

        if (!code) {
            return res.status(400).json({
                success: false,
                error: 'Code is required for test generation'
            });
        }

        console.log('🧪 AI Test Generation Request:', {
            codeLength: code.length,
            timestamp: new Date().toISOString()
        });

        const result = await aiCodeAnalysis.generateTests(code);

        console.log('✅ AI Test Generation Complete:', {
            success: result.success,
            hasTests: !!result.tests
        });

        res.json(result);
    } catch (error) {
        console.error('❌ AI Test Generation Error:', error);
        res.status(500).json({
            success: false,
            error: 'Internal server error during test generation',
            message: error.message
        });
    }
});

/**
 * @route GET /api/ai/features
 * @desc Get available AI code analysis features
 */
router.get('/features', (req, res) => {
    res.json({
        success: true,
        features: [
            {
                id: 'analyze-code',
                name: 'Code Analysis',
                description: 'Comprehensive code quality analysis with metrics and suggestions',
                endpoint: '/api/ai/analyze-code',
                methods: ['POST']
            },
            {
                id: 'optimize-code',
                name: 'Code Optimization',
                description: 'Performance and quality optimization suggestions',
                endpoint: '/api/ai/optimize-code',
                methods: ['POST'],
                parameters: ['optimizationType: performance|memory|quality|all']
            },
            {
                id: 'explain-code',
                name: 'Code Explanation',
                description: 'Detailed code explanation with concepts and algorithms',
                endpoint: '/api/ai/explain-code',
                methods: ['POST']
            },
            {
                id: 'detect-issues',
                name: 'Issue Detection',
                description: 'Bug and security issue detection with suggestions',
                endpoint: '/api/ai/detect-issues',
                methods: ['POST']
            },
            {
                id: 'generate-tests',
                name: 'Test Generation',
                description: 'Automated unit test generation for functions',
                endpoint: '/api/ai/generate-tests',
                methods: ['POST']
            }
        ],
        version: '1.0.0',
        status: 'active'
    });
});

module.exports = router;