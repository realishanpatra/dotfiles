return {
  {
    'gbprod/substitute.nvim',
    config = true,
    keys = {
      { 'S', function() require('substitute').visual() end, mode = 'x' },
      { 'S', function() require('substitute').operator() end, mode = 'n' },
      { 'X', function() require('substitute.exchange').operator() end, mode = 'n' },
      { 'X', function() require('substitute.exchange').visual() end, mode = 'x' },
      { 'Xc', function() require('substitute.exchange').cancel() end, mode = { 'n', 'x' } },
    },
  },
  {
    'monaqa/dial.nvim',
    keys = {
      { '<C-a>', '<Plug>(dial-increment)', mode = 'n' },
      { '<C-x>', '<Plug>(dial-decrement)', mode = 'n' },
      { '<C-a>', '<Plug>(dial-increment)', mode = 'v' },
      { '<C-x>', '<Plug>(dial-decrement)', mode = 'v' },
      { 'g<C-a>', 'g<Plug>(dial-increment)', mode = 'v' },
      { 'g<C-x>', 'g<Plug>(dial-decrement)', mode = 'v' },
    },
    config = function()
      local augend = require('dial.augend')
      local config = require('dial.config')

      local operators = augend.constant.new({
        elements = { '&&', '||' },
        word = false,
        cyclic = true,
      })

      local casing = augend.case.new({
        types = { 'camelCase', 'snake_case', 'PascalCase', 'SCREAMING_SNAKE_CASE' },
        cyclic = true,
      })

      config.augends:register_group({
        default = {
          augend.integer.alias.decimal,
          augend.integer.alias.hex,
          augend.date.alias['%Y/%m/%d'],
          augend.constant.alias.bool,
          casing,
        },
      })

      config.augends:on_filetype({
        go = {
          augend.integer.alias.decimal,
          augend.integer.alias.hex,
          augend.constant.alias.bool,
          operators,
        },
        typescript = {
          augend.integer.alias.decimal,
          augend.integer.alias.hex,
          augend.constant.alias.bool,
          augend.constant.new({ elements = { 'let', 'const' } }),
          casing,
        },
        markdown = {
          augend.integer.alias.decimal,
          augend.misc.alias.markdown_header,
        },
        yaml = {
          augend.integer.alias.decimal,
          augend.semver.alias.semver,
        },
        toml = {
          augend.integer.alias.decimal,
          augend.semver.alias.semver,
        },
      })
    end,
  },
  {
    'yetone/avante.nvim',
    event = 'VeryLazy',
    opts = {
      windows = {
        input = {
          prefix = '▷',
        },
        width = 40,
      },
    },
    build = 'make',
    dependencies = {
      'nvim-treesitter/nvim-treesitter',
      'stevearc/dressing.nvim',
      'nvim-lua/plenary.nvim',
      'MunifTanjim/nui.nvim',
      'nvim-tree/nvim-web-devicons',
      {
        'HakonHarnes/img-clip.nvim', -- support for image pasting
        event = 'VeryLazy',
        opts = {
          default = {
            embed_image_as_base64 = false,
            prompt_for_file_name = false,
            drag_and_drop = { insert_mode = true },
          },
        },
      },
      {
        'MeanderingProgrammer/render-markdown.nvim',
        ---@module 'render-markdown'
        ---@type render.md.UserConfig
        opts = { file_types = { 'markdown', 'Avante' } },
        ft = { 'markdown', 'Avante' },
      },
    },
  },
}
